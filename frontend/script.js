document.addEventListener('DOMContentLoaded', () => {

    /* --- 0. AUTHENTICATION & PROTECTION LOGIC --- */
    const currentPage = window.location.pathname.split('/').pop();
    const isLoginPage = currentPage === 'login.html' || currentPage === '';
    
    // Check login status
    const isLoggedIn = localStorage.getItem('aura_logged_in') === 'true';

    // 1. Protect Pages: Redirect to Login if not logged in
    if (!isLoginPage && !isLoggedIn) {
        window.location.href = 'login.html';
        return; 
    }

    // 2. Redirect to Dashboard if already logged in
    if (isLoginPage && isLoggedIn) {
        window.location.href = 'index.html';
        return;
    }

    // 3. Login/Signup Actions
    const btnLogin = document.getElementById('btn-login-action');
    const btnSignup = document.getElementById('btn-signup-action');

    if (btnLogin) {
        btnLogin.addEventListener('click', () => {
            localStorage.setItem('aura_logged_in', 'true');
            window.location.href = 'index.html';
        });
    }

    if (btnSignup) {
        btnSignup.addEventListener('click', () => {
            localStorage.setItem('aura_logged_in', 'true');
            window.location.href = 'index.html';
        });
    }

    // 4. Logout Action
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('aura_logged_in');
            window.location.href = 'login.html';
        });
    }

    // 5. Toggle Login/Signup Forms
    const viewSignin = document.getElementById('btn-signin-view');
    const viewSignup = document.getElementById('btn-signup-view');
    const formSignin = document.getElementById('form-signin');
    const formSignup = document.getElementById('form-signup');

    if (viewSignin && viewSignup) {
        viewSignin.addEventListener('click', () => {
            viewSignin.classList.add('active');
            viewSignup.classList.remove('active');
            formSignin.classList.add('active');
            formSignup.classList.remove('active');
        });

        viewSignup.addEventListener('click', () => {
            viewSignup.classList.add('active');
            viewSignin.classList.remove('active');
            formSignup.classList.add('active');
            formSignin.classList.remove('active');
        });
    }


    /* --- EXISTING UI LOGIC (Carousel, Hero, etc.) --- */
    
    const track = document.getElementById('track');
    const cards = document.querySelectorAll('.exercise-card');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');

    if (track && cards.length > 0) {
        let currentIndex = 0; 
        const cardWidth = 340; 
        
        function updateCarousel() {
            const offset = - (currentIndex * cardWidth) + (track.parentElement.offsetWidth / 2) - (150);
            track.style.transform = `translateX(${offset}px)`;

            cards.forEach((card, index) => {
                if (index === currentIndex) {
                    card.classList.add('active');
                    card.classList.remove('inactive');
                } else {
                    card.classList.remove('active');
                    card.classList.add('inactive');
                }
            });
        }

        nextBtn.addEventListener('click', () => {
            if (currentIndex < cards.length - 1) {
                currentIndex++;
                updateCarousel();
            }
        });

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });
        updateCarousel();


        /* HERO EXPANSION Logic */
        const overlay = document.getElementById('heroOverlay');
        const heroCard = document.getElementById('heroCard');
        const closeHero = document.getElementById('closeHero');
        
        const heroTitle = document.getElementById('heroTitle');
        const heroVisual = document.getElementById('heroVisual');
        const heroBadge = document.getElementById('heroBadge');

        cards.forEach((card, index) => {
            card.addEventListener('click', () => {
                if(currentIndex !== index) {
                    currentIndex = index;
                    updateCarousel();
                    return; 
                }
                const rect = card.getBoundingClientRect();
                
                heroTitle.innerText = card.querySelector('h2').innerText;
                heroVisual.innerText = card.dataset.icon || ""; 
                heroBadge.innerText = card.querySelector('.badge').innerText;
                
                heroCard.style.transition = 'none';
                heroCard.style.top = `${rect.top}px`;
                heroCard.style.left = `${rect.left}px`;
                heroCard.style.width = `${rect.width}px`;
                heroCard.style.height = `${rect.height}px`;
                heroCard.style.borderRadius = '24px';
                heroCard.style.gridTemplateColumns = '1fr'; 
                
                overlay.classList.add('active');
                void heroCard.offsetWidth; 

                heroCard.style.transition = ''; 
                heroCard.style.top = '10%';
                heroCard.style.left = '10%';
                heroCard.style.width = '80%';
                heroCard.style.height = '80%';
                heroCard.style.gridTemplateColumns = '40% 60%'; 
            });
        });

        closeHero.addEventListener('click', () => {
            overlay.classList.remove('active');
            setTimeout(() => { heroCard.style = ''; }, 500);
        });
    }

    /* Dynamic Date */
    const dateElement = document.getElementById('current-date');
    if(dateElement) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = new Date().toLocaleDateString('en-US', options);
    }





    /* --- OFFLINE "UNLIMITED" BOT LOGIC --- */
    const chatHistoryEl = document.getElementById('chat-history');
    const userInputEl = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    if (chatHistoryEl && userInputEl && sendBtn) {
        
        // 1. Load History
        let chatData = [];
        try {
            chatData = JSON.parse(localStorage.getItem('aura_chat_history')) || [];
        } catch (e) { chatData = []; }

        if (chatData.length === 0) {
            chatData = [{ sender: 'ai', text: "System Online. I am your local fitness assistant. Ask me about muscle groups, nutrition, or recovery strategies." }];
        }

        // 2. Render Chat
        function renderChat() {
            chatHistoryEl.innerHTML = '';
            chatData.forEach(msg => {
                const msgDiv = document.createElement('div');
                msgDiv.classList.add('message', msg.sender);
                msgDiv.innerHTML = msg.text; 
                chatHistoryEl.appendChild(msgDiv);
            });
            setTimeout(() => chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight, 10);
        }

        // 3. Add Message
        function addMessage(sender, text) {
            chatData.push({ sender, text });
            // Save last 50 messages
            if (chatData.length > 50) chatData = chatData.slice(chatData.length - 50);
            localStorage.setItem('aura_chat_history', JSON.stringify(chatData));
            renderChat();
        }

        // 4. THE BRAIN (Rule-Based Logic)
        function getBotResponse(input) {
            const text = input.toLowerCase();

            // --- GREETINGS ---
            if (text.match(/hi|hello|hey|start/)) return "Ready to train. What's your target today?";
            if (text.match(/bye|exit|quit/)) return "Session saved. Rest up!";
            
            // --- MUSCLE GROUPS & EXERCISES ---
            if (text.match(/chest|pecs|push/)) return "For **Chest**, focus on: <br>1. Bench Press (Strength)<br>2. Incline Dumbbell Press (Upper Chest)<br>3. Cable Flys (Isolation)<br>Keep shoulders retracted!";
            if (text.match(/back|lats|pull/)) return "For a wide **Back**: <br>1. Pull-ups (Width)<br>2. Barbell Rows (Thickness)<br>3. Lat Pulldowns.<br>Focus on driving elbows down.";
            if (text.match(/leg|squat|quad|hamstring/)) return "Don't skip **Leg Day**: <br>1. Squats (King of exercises)<br>2. Romanian Deadlifts (Hamstrings)<br>3. Leg Press.<br>Keep your core braced!";
            if (text.match(/arm|bicep|tricep/)) return "**Arms** Routine: <br>• Biceps: Barbell Curls & Hammer Curls.<br>• Triceps: Dips & Rope Pushdowns.<br>Control the eccentric (lowering) phase.";
            if (text.match(/abs|core|belly/)) return "**Core** stability is key. Try Planks (3x 60s), Hanging Leg Raises, and Cable Woodchoppers. Remember: Abs are revealed in the kitchen.";
            if (text.match(/shoulder|delts/)) return "**Shoulder** builder: <br>1. Overhead Press (Mass)<br>2. Lateral Raises (Width)<br>3. Face Pulls (Rear Delts/Health).";

            // --- NUTRITION ---
            if (text.match(/diet|food|eat|nutrition/)) return "Nutrition rule of thumb: Eat whole foods. 80% clean, 20% flexibility. Prioritize protein in every meal.";
            if (text.match(/protein|shake|whey/)) return "**Protein** builds muscle. Aim for 1.6g to 2.2g per kg of bodyweight. Good sources: Chicken, Fish, Eggs, Whey, Lentils.";
            if (text.match(/carb|energy|sugar/)) return "**Carbs** are fuel. Eat complex carbs (oats, rice, potatoes) around your workout window for maximum energy.";
            if (text.match(/fat|keto/)) return "Healthy **Fats** regulate hormones. Include avocado, nuts, olive oil, and salmon in your diet.";
            if (text.match(/weight loss|fat loss|cut/)) return "To **lose fat**: Caloric Deficit is required. Eat 300-500 calories below maintenance. High protein helps retain muscle while cutting.";
            if (text.match(/gain|bulk|muscle/)) return "To **build muscle**: Caloric Surplus. Eat 200-300 calories above maintenance. Focus on progressive overload in the gym.";

            // --- RECOVERY & HEALTH ---
            if (text.match(/sleep|rest|insomnia/)) return "Sleep is when you grow. Aim for **7-9 hours**. Keep your room cool and dark for better quality.";
            if (text.match(/water|hydrate|drink/)) return "**Hydration** affects strength. Drink 3-4 liters daily. If your urine is dark, drink more immediately.";
            if (text.match(/sore|pain|hurt|injury/)) return "⚠️ **Safety First**: If it's sharp pain, stop. If it's general soreness (DOMS), keep moving lightly and eat protein. Stretching helps.";
            if (text.match(/creatine|supplements/)) return "**Creatine Monohydrate** (5g/day) is the most researched supplement for power. Multivitamins and Fish Oil are also good basics.";

            // --- COMMANDS ---
            if (text === '/reset') {
                localStorage.removeItem('aura_chat_history');
                location.reload();
                return "Reseting system...";
            }

            // --- FALLBACK (If no keyword found) ---
            const fallbacks = [
                "Interesting. Tell me more about your goals.",
                "I see. Are you focusing on Strength or Hypertrophy?",
                "Could you be more specific? I can help with Exercises, Diet, or Recovery.",
                "Consistency is the key to progress. Keep showing up!",
                "Make sure to track your lifts to ensure Progressive Overload."
            ];
            return fallbacks[Math.floor(Math.random() * fallbacks.length)];
        }

        // 5. Handle Send
        function handleSend() {
            const text = userInputEl.value.trim();
            if (!text) return;

            addMessage('user', text);
            userInputEl.value = '';

            // Instant "Thinking" feel without network lag
            setTimeout(() => {
                const botResponse = getBotResponse(text);
                addMessage('ai', botResponse);
            }, 600); 
        }

        sendBtn.addEventListener('click', handleSend);
        userInputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSend();
        });

        renderChat();
    }
});