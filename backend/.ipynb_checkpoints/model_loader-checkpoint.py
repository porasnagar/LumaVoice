import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import logging

class ModelLoader:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.model_path = '/home/poras9868/predict_model.h5'
        self.encoder_path = '/home/poras9868/label_encoder.pkl'
        self.load_model()
        
    def load_model(self):
        """Load the trained model and label encoder"""
        try:
            # Load the Keras model
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                logging.info(f"Model loaded successfully from {self.model_path}")
                logging.info(f"Model input shape: {self.model.input_shape}")
                logging.info(f"Model output shape: {self.model.output_shape}")
            else:
                logging.warning(f"Model file {self.model_path} not found")
                
            # Load the label encoder/preprocessor
            if os.path.exists(self.encoder_path):
                with open(self.encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                logging.info(f"Label encoder loaded successfully from {self.encoder_path}")
                if hasattr(self.label_encoder, 'classes_'):
                    logging.info(f"Number of classes: {len(self.label_encoder.classes_)}")
                    logging.info(f"Sample classes: {self.label_encoder.classes_[:10]}")
            else:
                logging.warning(f"Encoder file {self.encoder_path} not found")
                
        except Exception as e:
            logging.error(f"Error loading model or encoder: {str(e)}")
            self.model = None
            self.label_encoder = None
    
    def predict(self, processed_frames, debug=False):
        """Make prediction on processed video frames using CTC decoding"""
        if self.model is None:
            return {
                'error': 'Model not loaded',
                'text': '',
                'confidence': 0.0
            }
        
        try:
            # Ensure input has correct shape
            input_data = np.array(processed_frames)
            if debug:
                logging.info(f"Input shape: {input_data.shape}")
                logging.info(f"Input range: [{input_data.min():.3f}, {input_data.max():.3f}]")
            
            # Make prediction
            predictions = self.model.predict(input_data, verbose=0)
            
            if debug:
                logging.info(f"Raw prediction shape: {predictions.shape}")
                logging.info(f"Raw prediction range: [{predictions.min():.6f}, {predictions.max():.6f}]")
                logging.info(f"Raw prediction sample (first 5 timesteps, first 10 classes):")
                logging.info(f"{predictions[0, :5, :10]}")
            
            # Check if this is a CTC model (3D output: batch, timesteps, classes)
            if len(predictions.shape) == 3:
                return self._decode_ctc_predictions(predictions, debug)
            
            # Handle 2D classification output (fallback)
            elif len(predictions.shape) == 2:
                return self._decode_classification_predictions(predictions, debug)
            
            else:
                return {
                    'text': 'Unsupported model output format',
                    'confidence': 0.0,
                    'raw_output': predictions.tolist()
                }
                
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            return {
                'error': f'Prediction failed: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def _decode_ctc_predictions(self, predictions, debug=False):
        """Decode CTC predictions to text"""
        try:
            batch_size = predictions.shape[0]
            sequence_length = predictions.shape[1]
            
            if debug:
                # Analyze prediction distribution
                max_indices = np.argmax(predictions[0], axis=1)
                unique_classes, counts = np.unique(max_indices, return_counts=True)
                logging.info(f"Dominant classes across {sequence_length} timesteps:")
                for cls, count in zip(unique_classes[:5], counts[:5]):  # Show top 5
                    if cls < len(self.label_encoder.classes_):
                        class_name = self.label_encoder.classes_[cls]
                        logging.info(f"  Class {cls} ('{class_name}'): {count} timesteps")
            
            # CTC decode using TensorFlow backend
            decoded, log_probs = tf.keras.backend.ctc_decode(
                predictions,
                input_length=np.ones(batch_size) * sequence_length,
                greedy=True
            )
            
            # Extract sequence for first (and likely only) batch item
            sequence = decoded[0].numpy()[0]
            log_prob = log_probs.numpy()[0]
            
            if debug:
                logging.info(f"CTC decoded sequence: {sequence}")
                logging.info(f"CTC log probability: {log_prob}")
            
            # Filter out blank tokens (typically -1 or a specific blank class)
            valid_indices = sequence[sequence >= 0]
            
            if len(valid_indices) == 0:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'decoded_sequence': sequence.tolist(),
                    'log_probability': float(log_prob)
                }
            
            # Convert indices to words using label encoder
            words = []
            for idx in valid_indices:
                try:
                    if idx < len(self.label_encoder.classes_):
                        word = self.label_encoder.classes_[idx]
                        words.append(word)
                        if debug:
                            logging.info(f"Index {idx} -> '{word}'")
                    else:
                        if debug:
                            logging.warning(f"Index {idx} out of range (max: {len(self.label_encoder.classes_)})")
                except Exception as e:
                    if debug:
                        logging.error(f"Error converting index {idx}: {e}")
                    continue
            
            predicted_text = ' '.join(words) if words else ''
            
            # Calculate confidence from log probability
            # Convert log probability to a more interpretable confidence score
            confidence = float(np.exp(log_prob)) if log_prob > -100 else 0.0
            confidence = min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
            
            result = {
                'text': predicted_text,
                'confidence': confidence,
                'decoded_sequence': sequence.tolist(),
                'valid_indices': valid_indices.tolist(),
                'words': words,
                'log_probability': float(log_prob)
            }
            
            if debug:
                logging.info(f"Final result: {result}")
            
            return result
            
        except Exception as e:
            logging.error(f"CTC decoding error: {str(e)}")
            return {
                'error': f'CTC decoding failed: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def _decode_classification_predictions(self, predictions, debug=False):
        """Decode classification predictions (fallback method)"""
        try:
            predicted_class_idx = np.argmax(predictions, axis=1)
            confidence = np.max(predictions, axis=1)
            
            if debug:
                logging.info(f"Classification - predicted indices: {predicted_class_idx}")
                logging.info(f"Classification - confidences: {confidence}")
            
            # Decode predictions using label encoder
            if self.label_encoder and hasattr(self.label_encoder, 'classes_'):
                try:
                    predicted_text = self.label_encoder.inverse_transform(predicted_class_idx)
                    text = ' '.join(predicted_text)
                except Exception as e:
                    logging.error(f"Error in inverse transform: {e}")
                    text = f"Class_{predicted_class_idx[0]}"
            else:
                text = f"Class_{predicted_class_idx[0]}"
            
            return {
                'text': text,
                'confidence': float(np.mean(confidence)),
                'predicted_indices': predicted_class_idx.tolist(),
                'frame_confidences': confidence.tolist()
            }
            
        except Exception as e:
            logging.error(f"Classification decoding error: {str(e)}")
            return {
                'error': f'Classification decoding failed: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def validate_input_shape(self, input_data):
        """Validate that input data matches model expectations"""
        if self.model is None:
            return False, "Model not loaded"
        
        expected_shape = self.model.input_shape
        actual_shape = input_data.shape
        
        if expected_shape[0] is None:  # Batch dimension can be flexible
            expected_shape = expected_shape[1:]
            actual_shape = actual_shape[1:]
        
        if actual_shape != expected_shape:
            return False, f"Shape mismatch: expected {expected_shape}, got {actual_shape}"
        
        return True, "Input shape valid"
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.model is None:
            return {
                'loaded': False,
                'type': 'None',
                'input_shape': None,
                'output_shape': None,
                'classes': 0
            }
        
        try:
            input_shape = self.model.input_shape
            output_shape = self.model.output_shape
            
            # Determine model type based on output shape
            if len(output_shape) == 3:
                model_type = 'CTC Sequence Model'
                num_classes = output_shape[2]
            elif len(output_shape) == 2:
                model_type = 'Classification Model'
                num_classes = output_shape[1]
            else:
                model_type = 'Unknown'
                num_classes = 1
            
            # Get label encoder info
            encoder_classes = 0
            if self.label_encoder and hasattr(self.label_encoder, 'classes_'):
                encoder_classes = len(self.label_encoder.classes_)
            
            return {
                'loaded': True,
                'type': model_type,
                'input_shape': input_shape,
                'output_shape': output_shape,
                'model_classes': num_classes,
                'encoder_classes': encoder_classes,
                'trainable_params': self.model.count_params(),
                'model_summary': str(self.model.summary()) if hasattr(self.model, 'summary') else 'N/A'
            }
            
        except Exception as e:
            return {
                'loaded': True,
                'type': 'Unknown',
                'error': str(e),
                'input_shape': None,
                'output_shape': None,
                'classes': 0
            }

    def test_prediction_pipeline(self, sample_input=None):
        """Test the prediction pipeline with sample data"""
        if self.model is None:
            return {'error': 'Model not loaded'}
        
        try:
            # Create sample input if not provided
            if sample_input is None:
                input_shape = self.model.input_shape
                if input_shape[0] is None:  # Remove batch dimension
                    shape = (1,) + input_shape[1:]
                else:
                    shape = input_shape
                sample_input = np.random.random(shape)
            
            logging.info(f"Testing with input shape: {sample_input.shape}")
            
            # Test prediction
            result = self.predict(sample_input, debug=True)
            
            return {
                'test_successful': True,
                'input_shape': sample_input.shape,
                'result': result
            }
            
        except Exception as e:
            return {
                'test_successful': False,
                'error': str(e)
            }


# Usage example and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize model loader
    loader = ModelLoader()
    
    # Get model info
    info = loader.get_model_info()
    print("Model Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test the pipeline
    test_result = loader.test_prediction_pipeline()
    print(f"\nPipeline Test: {test_result}")

    
# import os
# import pickle
# import numpy as np
# from tensorflow.keras.models import load_model
# import logging

# class ModelLoader:
#     def __init__(self):
#         self.model = None
#         self.label_encoder = None
#         self.model_path = '/home/poras9868/predict_model.h5'
#         self.encoder_path = '/home/poras9868/label_encoder.pkl'
#         self.load_model()
        
#     def load_model(self):
#         """Load the trained model and label encoder"""
#         try:
#             # Load the Keras model
#             if os.path.exists(self.model_path):
#                 self.model = load_model(self.model_path)
#                 logging.info(f"Model loaded successfully from {self.model_path}")
#             else:
#                 logging.warning(f"Model file {self.model_path} not found")
                
#             # Load the label encoder/preprocessor
#             if os.path.exists(self.encoder_path):
#                 with open(self.encoder_path, 'rb') as f:
#                     self.label_encoder = pickle.load(f)
#                 logging.info(f"Label encoder loaded successfully from {self.encoder_path}")
#             else:
#                 logging.warning(f"Encoder file {self.encoder_path} not found")
                
#         except Exception as e:
#             logging.error(f"Error loading model or encoder: {str(e)}")
#             self.model = None
#             self.label_encoder = None
    
#     def predict(self, processed_frames):
#         """Make prediction on processed video frames"""
#         if self.model is None:
#             return {
#                 'error': 'Model not loaded',
#                 'text': '',
#                 'confidence': 0.0
#             }
        
#         try:
#             # Prepare input for model
#             input_data = np.array(processed_frames)
            
#             # Make prediction
#             predictions = self.model.predict(input_data)
            
#             # Process predictions based on model output
#             if len(predictions.shape) == 2:  # Classification output
#                 predicted_class_idx = np.argmax(predictions, axis=1)
#                 confidence = np.max(predictions, axis=1)
                
#                 # Decode predictions using label encoder
#                 if self.label_encoder:
#                     predicted_text = self.label_encoder.inverse_transform(predicted_class_idx)
#                 else:
#                     predicted_text = [f"Class_{idx}" for idx in predicted_class_idx]
                
#                 return {
#                     'text': ' '.join(predicted_text),
#                     'confidence': float(np.mean(confidence)),
#                     'frame_predictions': predicted_text.tolist(),
#                     'frame_confidences': confidence.tolist()
#                 }
#             else:
#                 # Handle other model output formats
#                 return {
#                     'text': 'Raw prediction output',
#                     'confidence': 0.5,
#                     'raw_output': predictions.tolist()
#                 }
                
#         except Exception as e:
#             logging.error(f"Prediction error: {str(e)}")
#             return {
#                 'error': f'Prediction failed: {str(e)}',
#                 'text': '',
#                 'confidence': 0.0
#             }
    
#     def get_model_info(self):
#         """Get information about the loaded model"""
#         if self.model is None:
#             return {
#                 'loaded': False,
#                 'type': 'None',
#                 'input_shape': None,
#                 'classes': 0
#             }
        
#         try:
#             input_shape = self.model.input_shape
#             output_shape = self.model.output_shape
            
#             # Determine number of classes
#             if len(output_shape) == 2:
#                 num_classes = output_shape[1]
#             else:
#                 num_classes = 1
            
#             return {
#                 'loaded': True,
#                 'type': 'Keras Sequential/Functional',
#                 'input_shape': input_shape,
#                 'output_shape': output_shape,
#                 'classes': num_classes,
#                 'trainable_params': self.model.count_params()
#             }
#         except Exception as e:
#             return {
#                 'loaded': True,
#                 'type': 'Unknown',
#                 'error': str(e),
#                 'input_shape': None,
#                 'classes': 0
#             }