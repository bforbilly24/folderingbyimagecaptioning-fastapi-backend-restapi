import os
import shutil
from PIL import Image
import zipfile
import openpyxl
import numpy as np
import pickle
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from src.app.config.settings import (
    UPLOAD_DIR,
    OUTPUT_DIR,
    CATEGORY_PRIORITY,
    CATEGORY_KEYWORDS,
    BASE_DIR,
)
from src.app.services.ProgressTracker import progress_tracker

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ImageCaptionService:
    _instance = None
    _model = None
    _tokenizer = None
    _feature_extractor = None
    _max_length = 37
    _category_texts = {cat: " ".join(keywords) for cat, keywords in CATEGORY_KEYWORDS.items()}
    _smoothing_function = SmoothingFunction().method1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageCaptionService, cls).__new__(cls)
            model_path = os.path.join(BASE_DIR, "ml_models", "v2_image_captioning_resnet50_lstm.h5")
            if os.path.exists(model_path):
                cls._model = load_model(model_path)
            else:
                raise FileNotFoundError(f"Model file not found at {model_path}")
            tokenizer_path = os.path.join(BASE_DIR, "ml_models", "v2_tokenizer.pkl")
            if os.path.exists(tokenizer_path):
                with open(tokenizer_path, "rb") as f:
                    cls._tokenizer = pickle.load(f)
            else:
                raise FileNotFoundError(f"Tokenizer file not found at {tokenizer_path}")
            base_model = ResNet50(weights="imagenet")
            cls._feature_extractor = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
        return cls._instance

    def categorize_image_by_cosine(self, caption):
        """Menentukan kategori berdasarkan cosine similarity dengan prioritas."""
        caption_lower = caption.lower()

        # Compute cosine similarity
        vectorizer = TfidfVectorizer()
        text_data = [caption] + [self._category_texts[cat] for cat in CATEGORY_PRIORITY]
        tfidf_matrix = vectorizer.fit_transform(text_data)
        caption_vector = tfidf_matrix[0]
        category_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(caption_vector, category_vectors).flatten()

        # Store similarity scores
        similarity_dict = dict(zip(CATEGORY_PRIORITY, similarities))

        # Select category with highest similarity, respecting priority
        selected_category = CATEGORY_PRIORITY[0]
        max_similarity = -1
        for cat in CATEGORY_PRIORITY:
            if similarity_dict[cat] > max_similarity:
                max_similarity = similarity_dict[cat]
                selected_category = cat

        # Log details for debugging
        logging.info(f"Caption: '{caption}', Similarity scores: {similarity_dict}")

        # Apply threshold for categorization
        if max_similarity < 0.05:
            logging.info(f"Caption: '{caption}' categorized as 'tidak dikategorikan' (score: {max_similarity:.4f})")
            return "tidak dikategorikan", max_similarity
        logging.info(f"Caption: '{caption}' categorized as '{selected_category}' (score: {max_similarity:.4f})")
        return selected_category, max_similarity

    def _compute_bleu_score(self, caption, category):
        """Menghitung BLEU-1 score untuk caption terhadap kata kunci kategori."""
        caption_tokens = caption.lower().split()

        # Jika kategori adalah 'tidak dikategorikan', gunakan semua kata kunci dari semua kategori
        if category == "tidak dikategorikan":
            reference_tokens = [word for keywords in CATEGORY_KEYWORDS.values() for word in keywords]
            references = [reference_tokens]  # BLEU membutuhkan list of lists
        else:
            references = [CATEGORY_KEYWORDS[category]]  # Kata kunci kategori sebagai referensi

        # Hitung BLEU-1 score dengan smoothing
        bleu_score = sentence_bleu(references, caption_tokens, weights=(1, 0, 0, 0), smoothing_function=self._smoothing_function)
        return bleu_score

    def _preprocess_image(self, image_path):
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        features = self._feature_extractor.predict(img_array, verbose=0)
        return features

    def _generate_caption(self, image_feature):
        in_text = "startseq"
        for _ in range(self._max_length):
            sequence = self._tokenizer.texts_to_sequences([in_text])[0]
            sequence = pad_sequences([sequence], maxlen=self._max_length)
            if len(image_feature.shape) == 2:
                image_feature_input = image_feature
            else:
                raise ValueError(f"Unexpected image_feature shape: {image_feature.shape}")
            if len(sequence.shape) == 2:
                sequence_input = sequence
            else:
                raise ValueError(f"Unexpected sequence shape: {sequence.shape}")
            yhat = self._model.predict([image_feature_input, sequence_input], verbose=0)
            yhat = np.argmax(yhat)
            word = self._idx_to_word(yhat)
            if word is None or word == "endseq":
                break
            in_text += " " + word
        caption = in_text.replace("startseq", "").strip()
        return caption

    def _idx_to_word(self, integer):
        for word, index in self._tokenizer.word_index.items():
            if index == integer:
                return word
        return None

    def process_images(self, files, task_id: str = None):
        if task_id:
            progress_tracker.update_step(task_id, 0, "processing")  # Initializing
        
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if task_id:
            progress_tracker.update_step(task_id, 0, "completed")
            progress_tracker.update_step(task_id, 1, "processing")  # Loading models

        # Models are already loaded in __new__, so mark as completed
        if task_id:
            progress_tracker.update_step(task_id, 1, "completed")
            progress_tracker.update_step(task_id, 2, "processing")  # Extracting features

        image_data = []
        total_files = len(files)
        
        for i, file in enumerate(files):
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Update progress for feature extraction
            if task_id and i == 0:
                progress_tracker.update_step(task_id, 2, "completed")
                progress_tracker.update_step(task_id, 3, "processing")  # Generating captions

            image_feature = self._preprocess_image(file_path)
            caption = self._generate_caption(image_feature)
            
            # Update progress for categorization
            if task_id and i == 0:
                progress_tracker.update_step(task_id, 3, "completed")
                progress_tracker.update_step(task_id, 4, "processing")  # Categorizing

            category, cosine_similarity = self.categorize_image_by_cosine(caption)
            bleu_score = self._compute_bleu_score(caption, category)

            # Update progress for organizing
            if task_id and i == 0:
                progress_tracker.update_step(task_id, 4, "completed")
                progress_tracker.update_step(task_id, 5, "processing")  # Organizing folders

            folder_path = os.path.join(OUTPUT_DIR, category)
            os.makedirs(folder_path, exist_ok=True)
            shutil.move(file_path, os.path.join(folder_path, file.filename))

            image_data.append({
                "filename": file.filename,
                "caption": caption,
                "category": category,
                "cosine_similarity": round(cosine_similarity, 4),
                "bleu_score": round(bleu_score, 4)
            })

        if task_id:
            progress_tracker.update_step(task_id, 5, "completed")
            progress_tracker.update_step(task_id, 6, "processing")  # Creating Excel

        self._generate_excel(image_data)
        
        if task_id:
            progress_tracker.update_step(task_id, 6, "completed")
            progress_tracker.update_step(task_id, 7, "processing")  # Generating ZIP

        zip_path = self._generate_zip()

        if task_id:
            progress_tracker.update_step(task_id, 7, "completed")
            progress_tracker.update_step(task_id, 8, "processing")  # Completing

        # Cleanup: Hapus semua kecuali ZIP
        for item in os.listdir(OUTPUT_DIR):
            item_path = os.path.join(OUTPUT_DIR, item)
            if item_path != zip_path:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                elif os.path.isfile(item_path):
                    os.remove(item_path)

        if task_id:
            progress_tracker.update_step(task_id, 8, "completed")

        return zip_path, image_data

    def _generate_excel(self, image_data):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Image Categorization"
        ws.append(["Filename", "Caption", "Category", "Cosine Similarity Score", "BLEU-1 Score"])
        for data in image_data:
            ws.append([
                data["filename"],
                data["caption"],
                data["category"],
                data["cosine_similarity"],
                data["bleu_score"]
            ])
        wb.save(os.path.join(OUTPUT_DIR, "detail_folderisasi.xlsx"))

    def _generate_zip(self):
        zip_path = os.path.join(OUTPUT_DIR, "hasil_folderisasi.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(OUTPUT_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path != zip_path:
                        arcname = os.path.relpath(file_path, OUTPUT_DIR)
                        zipf.write(file_path, arcname)
        return zip_path

    def process_folder(self, folder_path: str, task_id: str = None):
        """Process all images in a folder and its subdirectories"""
        if task_id:
            progress_tracker.update_step(task_id, 0, "processing")  # Initializing
            
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        if task_id:
            progress_tracker.update_step(task_id, 0, "completed")
            progress_tracker.update_step(task_id, 1, "processing")  # Loading models

        # Models already loaded
        if task_id:
            progress_tracker.update_step(task_id, 1, "completed")
            progress_tracker.update_step(task_id, 2, "processing")  # Scanning folder
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        image_data = []
        processed_count = 0
        
        # Count total images first for better progress tracking
        total_images = 0
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    total_images += 1
        
        if task_id:
            progress_tracker.update_step(task_id, 2, "completed")
            progress_tracker.update_step(task_id, 3, "processing")  # Extracting features
        
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in image_extensions:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # Update progress for first image
                        if task_id and processed_count == 0:
                            progress_tracker.update_step(task_id, 3, "completed")
                            progress_tracker.update_step(task_id, 4, "processing")  # Generating captions
                        
                        image_feature = self._preprocess_image(file_path)
                        caption = self._generate_caption(image_feature)
                        
                        # Update progress for categorization
                        if task_id and processed_count == 0:
                            progress_tracker.update_step(task_id, 4, "completed")
                            progress_tracker.update_step(task_id, 5, "processing")  # Categorizing
                        
                        category, cosine_similarity = self.categorize_image_by_cosine(caption)
                        bleu_score = self._compute_bleu_score(caption, category)

                        # Update progress for organizing
                        if task_id and processed_count == 0:
                            progress_tracker.update_step(task_id, 5, "completed")
                            progress_tracker.update_step(task_id, 6, "processing")  # Organizing folders

                        # Create category folder and copy image
                        folder_path_out = os.path.join(OUTPUT_DIR, category)
                        os.makedirs(folder_path_out, exist_ok=True)
                        shutil.copy2(file_path, os.path.join(folder_path_out, filename))

                        image_data.append({
                            "filename": filename,
                            "caption": caption,
                            "category": category,
                            "cosine_similarity": round(cosine_similarity, 4),
                            "bleu_score": round(bleu_score, 4)
                        })
                        
                        processed_count += 1
                        logging.info(f"Processed: {filename} ({processed_count}/{total_images})")
                        
                    except Exception as e:
                        logging.error(f"Error processing {filename}: {e}")
                        continue

        if image_data:
            if task_id:
                progress_tracker.update_step(task_id, 6, "completed")
                progress_tracker.update_step(task_id, 7, "processing")  # Creating Excel
                
            self._generate_excel(image_data)
            
            if task_id:
                progress_tracker.update_step(task_id, 7, "completed")
                progress_tracker.update_step(task_id, 8, "processing")  # Generating ZIP
                
            zip_path = self._generate_zip()

            if task_id:
                progress_tracker.update_step(task_id, 8, "completed")
                progress_tracker.update_step(task_id, 9, "processing")  # Completing

            # Cleanup: Remove all except ZIP
            for item in os.listdir(OUTPUT_DIR):
                item_path = os.path.join(OUTPUT_DIR, item)
                if item_path != zip_path:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    elif os.path.isfile(item_path):
                        os.remove(item_path)

            if task_id:
                progress_tracker.update_step(task_id, 9, "completed")

            return zip_path, processed_count, image_data
        
        return None, 0, []