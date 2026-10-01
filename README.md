# Dexora 🤟

Ever wondered, "If only I had learned sign language growing up"?  
Or just wanted to learn sign language, but studying each and every sign was daunting?

Presenting **Dexora**, an interactive, gesture-based system. This project turns your webcam into an interactive ASL learning buddy using OpenCV + MediaPipe + Machine Learning.

## But what can it do?
- Watches your hands in real-time: Your webcam tracks hand movements to detect signs.
- Turns learning into a game 🎯: Get a random word and Sign it out
- Tracks progress overtime, managing the difficulty levels

## Under the Hood (the Tech Stack 💻)
OpenCV - camera + image processing  
MediaPipe - hand tracking magic  
ML Model - predicts ASL gestures  
Smoothing logic - stops flickering predictions  
Custom gesture handling - makes interaction natural  

## 📂 Project Layout:
```
asl-project/  
├── main.py                # Runs everything  
├── core/                 # Brain of the system  
├── handlers/             # Gesture logic  
├── gestures/             # Special gestures (like exit)  
├── models/               # Trained ML model  
```

## Want to give Dexora a try yourself? Setup:
```
git clone https://github.com/KetakiJ18/asl_trainer.git
cd asl-project
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### How to use Dexora?
- run
``` python main.py```  
- Sign and build the word given or request a new word.
- To use a new word or submit the current word, hover over their respective buttons
- To add spaces hold up both palms opened
- To backspace, wipe from right to left 
- To exit the app, connect both index fingers and hold. 
**IT'S THAT EASY**

## 🔮 The stuff in pipeline:
📚 Step-by-step ASL lessons (A–Z, numbers)  
💡 Hint system during challenges  
📊 Progress tracking  
🧾 Full sentence recognition  
🌐 Maybe a web version ??! 👀

## 💬 Why This Exists?
Because why do we not learn Sign Language as a universal language?  
Because learning ASL should feel interactive intuitive  
and honestly… kinda fun