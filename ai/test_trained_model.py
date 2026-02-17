"""
Test Trained Chat GPT-2 Model
Tests the custom-trained chat model on various inputs
"""
import os
import sys
import json
import torch
from datetime import datetime
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class TrainedChatTester:
    """Test the trained chat model"""
    
    def __init__(self, model_path="ai/trained_models/final_chat_model/trained_chat_model_1.0"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load trained model
        self.load_trained_model()
        
    def load_trained_model(self):
        """Load the trained model and tokenizer"""
        
        print(f"🤖 Loading trained model from: {self.model_path}")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Trained model not found at: {self.model_path}")
        
        # Load tokenizer and model
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_path)
        self.model = GPT2LMHeadModel.from_pretrained(self.model_path)
        
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Model loaded successfully on {self.device}")
        print(f"📊 Vocab size: {len(self.tokenizer)}")
        
        # Load metadata
        metadata_path = os.path.join(self.model_path, "training_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                print(f"📋 Model trained on: {metadata.get('trained_on', 'Unknown')}")
                print(f"🎯 Training examples: {metadata.get('training_params', {}).get('num_examples', 'Unknown')}")
    
    def generate_response(self, client_message, max_length=100):
        """Generate freelancer response to client message"""
        
        # Format input like training data
        prompt = f"<|startoftext|>\n<|client|> {client_message}\n<|freelancer|>"
        
        # Tokenize
        inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.encode("<|endoftext|>")[0]
            )
        
        # Decode and extract response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the freelancer response
        freelancer_start = full_response.find("<|freelancer|>") + len("<|freelancer|>")
        response = full_response[freelancer_start:].strip()
        
        # Clean up
        if "<|endoftext|>" in response:
            response = response.split("<|endoftext|>")[0]
        if "<|client|>" in response:
            response = response.split("<|client|>")[0]
            
        return response.strip()
    
    def test_conversations(self):
        """Test various conversation scenarios"""
        
        test_cases = [
            {
                "scenario": "💼 Project Inquiry", 
                "client_message": "Hello! Are you available for a writing project?"
            },
            {
                "scenario": "💰 Rate Discussion",
                "client_message": "What's your rate for 2000-word articles?"
            },
            {
                "scenario": "⏰ Deadline Question",
                "client_message": "Can you deliver 3 articles by Monday?"
            },
            {
                "scenario": "🌍 Language Requirement",
                "client_message": "We need content in Dutch for our casino website."
            },
            {
                "scenario": "📋 Content Type",
                "client_message": "We need casino reviews and slot descriptions."
            },
            {
                "scenario": "🎯 SEO Requirements",
                "client_message": "The content needs to be SEO-optimized with specific keywords."
            },
            {
                "scenario": "📄 Sample Request",
                "client_message": "Can you provide some writing samples?"
            },
            {
                "scenario": "💳 Payment Terms",
                "client_message": "What are your payment terms and methods?"
            }
        ]
        
        print(f"\n🧪 Testing Trained Model with {len(test_cases)} scenarios")
        print("=" * 80)
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. {test['scenario']}")
            print(f"👩‍💼 Client: {test['client_message']}")
            
            # Generate response
            try:
                response = self.generate_response(test['client_message'])
                print(f"👨‍💻 Freelancer (Trained Model): {response}")
                
            except Exception as e:
                print(f"❌ Error generating response: {str(e)}")
            
            print("-" * 40)
        
        print(f"\n✅ Testing completed!")

def main():
    """Main testing function"""
    
    try:
        print("🧪 Testing Trained Chat GPT-2 Model")
        print("=" * 50)
        
        # Initialize tester
        tester = TrainedChatTester()
        
        # Run tests
        tester.test_conversations()
        
        # Interactive mode
        print(f"\n🎮 Interactive Mode - Type 'quit' to exit")
        print("-" * 40)
        
        while True:
            client_input = input("\n👩‍💼 Client message: ").strip()
            
            if client_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if client_input:
                try:
                    response = tester.generate_response(client_input)
                    print(f"👨‍💻 Freelancer: {response}")
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
        
        print("\n👋 Testing session ended!")
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 Testing successful!' if success else '❌ Testing failed!'}")