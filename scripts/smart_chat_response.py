"""
Smart Chat Response Generator - CLEAN VERSION
Phase Detection: BERT AI only (no keywords, no fallbacks)
Response Modes: Template OR AI (GPT-2)
"""
import sys
import os
import json
import argparse
from datetime import datetime
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Set UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path and import database manager
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.chat_database_manager import ChatDatabase

# class that connects to database initializes templates, and implements AI chat response generation
class SmartChatResponse:
    """Simple phase-based response generator with BERT AI"""

    # class for AI model GPT-2 text generation
    # it has __init__ and generate_single_response functions
    # __init__ loads model and tokenizer
    # generate_single_response generates text based on prompt
    class ChatGPT2Generator:
        """Simplified GPT-2 generator integrated into SmartChatResponse"""
        # loads components for GPT-2 model
        # 1. set model path based on trained model if available else use base GPT-2
        # 2. load tokenizer from model path
        # 3. load model from model path
        # 4. set pad token if not set
        # 5. set hardware device to choose CUDA if available else CPU
        # 6. load model to hardware device and set to eval mode
        def __init__(self):
            print("Loading GPT-2...")
            # Check for trained model first
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            trained_model_path = os.path.join(project_root, "ai", "chat_bot_trainer", "trained_models", "final_chat_model", "trained_chat_model_1.0")
            # if trained model is found set model_path to it
            if os.path.exists(trained_model_path):
                print("🎯 Using TRAINED model for better responses")
                model_path = trained_model_path
            # else set model_path to base GPT-2
            else:
                print("⚠️ Trained model not found, using base GPT-2")
                model_path = "gpt2"
            
            # Load tokenizer
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            # load model
            self.model = GPT2LMHeadModel.from_pretrained(model_path)
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Set hardware device to use CUDA if available else CPU
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            # load model to hardware device
            self.model.to(self.device)
            # set model to eval mode
            self.model.eval()
            print("✅ GPT-2 Ready")
        # function to generate response
        # takes prompt and max_length as input
        # 1. encode prompt using tokenizer and move to hardware device
        # 2. generate outputs with model.generate using parameters for text generation
        # 3. decode generated outputs to text
        # 4. simple cleanup to ensure proper ending punctuation     
        def generate_single_response(self, prompt, max_length=80):
            """Simple GPT-2 text generation"""
            try:
                # tokenize prompt and move to hardware device
                inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
                # generate outputs with the initialized model
                # use torch.no_grad because no training is happening only inference
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=inputs.shape[1] + max_length,
                        temperature=0.7,
                        do_sample=True,
                        top_p=0.9,
                        pad_token_id=self.tokenizer.eos_token_id,
                        no_repeat_ngram_size=2
                    )
                # decode generated outputs to text
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # extract response part
                response = generated_text[len(prompt):].strip()
                
                # Simple cleanup
                if not response.endswith(('.', '!', '?')) and len(response) > 10:
                    response = response.rsplit(' ', 1)[0] + '.'
                
                return response[:150] if len(response) > 150 else response
                
            except Exception as e:
                print(f"GPT-2 Error: {e}")
                return "Thank you for your message."
    # templates dict for each phase (detected by BERT AI)
    # NOTE: Only 8 phases match trained BERT model - extras removed for clarity
    # and one fallback 'general_inquiry' added
    TEMPLATES = {
        'initial_response': [
            "Thank you for reaching out! I'm very interested. Could you tell me more about the project?",
            "Good day! I'm available. What are the main deliverables?",
            "Hello! I'd be happy to help. Can you share more details?"
        ],
        'ask_details': [
            "Could you provide more details about the project scope?",
            "What specific requirements do you have in mind?",
            "I'd love to learn more about what you're looking for!"
        ],
        'knowledge_check': [
            "Yes, I have extensive experience with that topic. Let me show you my expertise.",
            "Absolutely! I'm well-versed in that area. Would you like some examples?",
            "I'm confident in handling that subject. What specific aspects interest you?"
        ],
        'language_confirm': [
            "I'm fluent in both languages. Which would you prefer for this project?",
            "I can work in either language comfortably. What's your preference?",
            "Both languages work for me. Which fits your target audience better?"
        ],
        'rate_negotiation': [
            "That rate works perfectly for me. When can we start?",
            "I'm comfortable with that pricing. What's the next step?",
            "Great! That rate is acceptable. Should we proceed with the contract?"
        ],
        'deadline_samples': [
            "Absolutely! I can deliver by that deadline. Should I start immediately?",
            "Yes, that timeline works perfectly. I'll prioritize your project.",
            "I can definitely meet that deadline. Let's get started!"
        ],
        'structure_clarification': [
            "Perfect! I understand the structure requirements. I'll follow that format exactly.",
            "Got it! I'll include all those elements in the proper structure.",
            "Understood! I'll make sure each piece follows that exact format."
        ],
        'contract_acceptance': [
            "Contract accepted! Starting work now. You'll have it by the deadline.",
            "Thank you! I've accepted and will begin immediately.",
            "Great! Contract signed. I'm diving into the first batch now."
        ],
        # Fallback for unknown phases or errors
        'general_inquiry': [
            "Could you provide more details about what you're looking for?",
            "I'd be glad to assist! Can you clarify what you need?",
            "Let me know the specifics and I'll help!"
        ]
    }
    # funtion that initialises variables
    #1. var to hold project root
    #2. var to hold path to database
    #3. var for database
    def __init__(self):
        """Initialize response generator (no phase detection)"""
        # var to hold project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # var to hold path to database
        db_path = os.path.join(project_root, "data", "chat_data.db")
        # var for database
        self.db = ChatDatabase(db_path)
        
        print("\n" + "="*60)
        print("INITIALIZING SMART CHAT RESPONSE")
        print("="*60)
        print("✅ RESPONSE GENERATOR ACTIVE")
        print("   Phase detection: Standalone (from database)")
        print("   Template responses: 8 phases")
        print("   AI responses: GPT-2")
        print("="*60 + "\n")
        
        print("="*60 + "\n")
    # funtion that takes latest session_id and max_messages as input
    # takes latest session from database by session_id search
    # and returns context which is dictionary of messages key sender_type and text value
    # and session_id
    def get_context(self, session_id, max_messages=10):
        """Get conversation context from database"""
        # check for latest session
        if session_id == "latest":
            # get latest session wtih db manager function with var for database
            latest = self.db.get_latest_session()
            # put latest session id in session_id variable
            session_id = latest['session_id'] if latest else None
        # if there are no session_id return empty
        if not session_id:
            return "", None
        # get recent messages from database manager with session_id var earlier initialized
        # and return messages as context limiting to max_messages var that is passed
        messages = self.db.get_recent_messages(session_id, limit=max_messages)
        # make dictionary of messages
        context = "\n".join([f"{m['sender_type']}: {m['text']}" for m in messages])
        return context, session_id

    # function that takes phase as input and generates template responses based on phase
    # takes phase and num_options as input
    # 1. gets template responses (3) for phase if not found uses general_inquiry templates
    # 2. returns list of template responses up to num_options or available templates
    def generate_template_response(self, phase, num_options=3):
        """Generate template responses"""
        templates = self.TEMPLATES.get(phase, self.TEMPLATES['general_inquiry'])
        # imside template responses for phase return lesser numer => num_options or available templates
        return templates[:min(num_options, len(templates))]
    # function to save results to temp file for dashboard
    # takes result dict as input, result is output of generate() function
    #1. var to hold temp file path
    #2. temp data structure compatible with dashboard to hold suggestions
    #3. based on result content append appropriate fields to temp_data
    def save_to_temp_file(self, result):
        """Save results to temp file for dashboard"""
        try:
            # var to hold temp file path
            temp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_ai_suggestions.json')

            # Create temp data structure compatible with dashboard to hold suggestions
            temp_data = {
                'session_id': result['session_id'],
                'phase': result['phase'],
                'confidence': result['confidence'],
                'model_used': 'bert_phase_detector',
                'created_at': datetime.now().isoformat()
            }
            # append temp_data with results content
            # if argument is template_response
            # suggestion_type
            # template_response 
            # ai_response
            if 'template_response' in result and 'ai_response' in result:
                # Both mode
                temp_data['suggestion_type'] = 'both'
                temp_data['template_response'] = result['template_response']
                temp_data['ai_response'] = result['ai_response']
            # else if argument is responses
            # suggestion_type
            # responses
            elif 'responses' in result:
                # Template or AI mode
                temp_data['suggestion_type'] = result.get('mode', 'template')
                temp_data['responses'] = result['responses']
            
            # Save to file
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=2)
            # log it  
            print(f"[SAVE] Results saved to temp_ai_suggestions.json")
            
        except Exception as e:
            print(f"[WARN] Failed to save temp file: {e}")

    # function that takes phase as input and generates AI response using GPT-2
    # takes phase, context and session_id as input
    # 1. try to import ChatGPT2Generator from ai.chat_gpt2_generator
    # 2. puts ChatGPT2Generator in gpt2 variable
    # 3. create detailed prompt which includes context and phase information
    # 4. call gpt2.generate_single_response with custom_prompt
    # 5. if successful return first response
    # 6. else return AI failure message
    def generate_ai_response(self, phase, context, session_id):
        """Generate AI response using integrated GPT-2"""
        try:
            # Use internal GPT-2 generator
            if not hasattr(self, '_gpt2_generator'):
                self._gpt2_generator = self.ChatGPT2Generator()
            
            # Create detailed prompt for better GPT-2 response
            prompt = f"""You are a professional freelancer responding to a client in an Upwork chat conversation.

CONVERSATION CONTEXT:
{context[-500:]}

AI PHASE DETECTION RESULT:
The AI system has analyzed this conversation and detected that the client is in the "{phase}" phase.

PHASE MEANINGS:
- initial_response: Client is asking if you're available for work
- ask_details: Client wants more information about project scope  
- knowledge_check: Client is testing your expertise in specific topics
- language_confirm: Client is asking about language preferences
- rate_negotiation: Client is discussing pricing and budget
- deadline_samples: Client is asking about delivery timelines
- structure_clarification: Client wants to know about content format/structure
- contract_acceptance: Client is ready to hire and wants you to accept contract

YOUR TASK:
Write a professional, friendly response that addresses the "{phase}" phase appropriately. 
- Keep it concise (1-3 sentences)
- Sound natural and conversational
- Be enthusiastic and professional
- Directly address what the client needs in this phase

Response:"""
            
            # Generate response using internal GPT-2
            ai_response = self._gpt2_generator.generate_single_response(prompt)
            
            # Return response or error message
            if ai_response:
                return ai_response
            else:
                return "[AI Error] GPT-2 response generation failed. Please try again or use template mode."
        except Exception as e:
            print(f"[WARN] GPT-2 failed: {e}")
            return f"[AI Error] GPT-2 crashed: {str(e)}. Please use template mode instead."
    # function that generates response
    # takes inputs ===============================================
    # session_id from database or 'latest'
    # mode - template, ai or both from main() argparser
    # num_options - number of template options to generate from main() argparser
    # =======================================================
    # 1. Get session with pre-detected phase from database
    # 2. extract phase and confidence from session_data that was fetched with session_id
    # 3. Generate response based on mode (template or AI)
    def generate(self, session_id='latest', mode='template', num_options=3):
        """
        Main generation function - NEW VERSION
        
        1. Get session with pre-detected phase from database
        2. Generate response based on mode (template or AI)
        3. NO phase detection here - phase must be detected first!
        """
        
        # Get session with phase from database
        if session_id == 'latest':
            latest = self.db.get_latest_session()
            if latest:
                session_id = latest['session_id']
            else:
                return {'success': False, 'error': 'No active sessions found'}
        
        if not session_id:
            return {'success': False, 'error': 'No session ID provided'}
        
        # get session with phase that phase detector stored in database earlier
        session_data = self.db.get_session_with_phase(session_id)
        
        if not session_data:
            return {'success': False, 'error': f'Session {session_id} not found'}
        # if phase not detected return error
        if not session_data.get('phase'):
            return {
                'success': False, 
                'error': 'Phase not detected yet. Run standalone phase detector first.',
                'session_id': session_id
            }
        # extract phase and confidence from session_data that was fetched with session_id
        phase = session_data['phase']
        confidence = session_data['phase_confidence']
        
        print(f"\n[PHASE] {phase} ({confidence:.1%} confidence) - from database")
        print(f"[SESSION] {session_id}")
        
        # if mode is set to ai or both
        if mode in ['ai', 'both']:
            # get context for AI generation
            messages = self.db.get_recent_messages(session_id, limit=10)
            context = "\n".join([f"{m['sender_type']}: {m['text']}" for m in messages])
            # else return empty string because only AI uses context
        else:
            context = ""
        
        # Generate response based on mode
        # if template mode
        if mode == 'template':
            # response is generated template responses for phase
            responses = self.generate_template_response(phase, num_options)
            print(f"[MODE] Template ({len(responses)} options)")
            # elif mode is ai
        elif mode == 'ai':
            # response is generated AI response for phase and context
            ai_response = self.generate_ai_response(phase, context, session_id)
            responses = [ai_response]
            print(f"[MODE] AI (GPT-2)")
            # if mode is both
        elif mode == 'both':
            template_response = self.generate_template_response(phase, 1)[0]
            ai_response = self.generate_ai_response(phase, context, session_id)
            print(f"[MODE] Both (Template + AI)")
            # inside resulty put response and other fields
            result = {
                'success': True,
                'phase': phase,
                'confidence': confidence,
                'template_response': template_response,
                'ai_response': ai_response,
                'session_id': session_id
            }
            # Save to temp file for dashboard
            self.save_to_temp_file(result)
            return result
        # else return error for invalid mode
        else:
            return {'success': False, 'error': f'Invalid mode: {mode}'}
        
        result = {
            'success': True,
            'session_id': session_id,
            'mode': mode,
            'phase': phase,
            'confidence': confidence,
            'responses': responses,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to temp file for dashboard
        self.save_to_temp_file(result)
        return result
# main function
# 1. takes arguments that you pass from command line
# 2. make result var for SmartChatResponse class instance and put arguments or defaults to generate function
# 3. Return JSON for n8n stdout of result var
# 5. log everything for debugging
def main():
    # inside main set mode and num_options, session_id, also set defaults
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Smart Chat Response')
    parser.add_argument('--session-id', default='latest')
    parser.add_argument('--mode', choices=['template', 'ai', 'both'], default='template')
    parser.add_argument('--num-options', type=int, default=3)
    # inside var put all the arguments from argparser
    args = parser.parse_args()
    
    try:
        # inside var put SmartChatResponse class instance
        generator = SmartChatResponse()
        # feed the arguments to generate function of SmartChatResponse instance generator
        result = generator.generate(args.session_id, args.mode, args.num_options)
        # log everything for debugging
        print("\n" + "="*60)
        if result['success']:
            print(f"Phase: {result['phase']} ({result['confidence']:.1%})")
            
            if args.mode == 'both':
                print(f"\nTemplate Response:")
                print(f"• {result['template_response']}\n")
                print(f"AI Response:")
                print(f"• {result['ai_response']}\n")
            else:
                print(f"\nResponses:\n")
                for i, resp in enumerate(result['responses'], 1):
                    print(f"{i}. {resp}\n")
        else:
            print(f"Error: {result['error']}")
        print("="*60)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['success'] else 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
