// FAQ Accordion
document.querySelectorAll('.accordion-header').forEach(button => {
    button.addEventListener('click', () => {
        const accordionItem = button.parentElement;
        const isOpen = accordionItem.classList.contains('active');

        // Close all other items
        document.querySelectorAll('.accordion-item').forEach(item => {
            item.classList.remove('active');
            item.querySelector('span').textContent = '+';
        });

        if (!isOpen) {
            accordionItem.classList.add('active');
            button.querySelector('span').textContent = '−';
        }
    });
});

// Counter Animation
const observerOptions = {
    threshold: 0.5
};

const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const counter = entry.target;
            const target = parseInt(counter.getAttribute('data-target'));
            let current = 0;
            const increment = target / 50;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.innerText = Math.ceil(current);
                    setTimeout(updateCounter, 20);
                } else {
                    counter.innerText = target;
                }
            };

            updateCounter();
            observer.unobserve(counter);
        }
    });
}, observerOptions);

document.querySelectorAll('.counter-num').forEach(counter => {
    counterObserver.observe(counter);
});

// Form Submission (Real Telegram Integration)
document.getElementById('contactForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const originalText = btn.innerText;

    // --- НАСТРОЙКИ ТЕЛЕГРАМА ---
    const BOT_TOKEN = 'ВАШ_ТОКЕН_БОТА'; // Получить у @BotFather
    const CHAT_ID = 'ВАШ_CHAT_ID';     // Получить у @userinfobot
    // ---------------------------

    const formData = new FormData(e.target);
    const name = e.target.querySelector('input[placeholder="Ваше имя"]').value;
    const phone = e.target.querySelector('input[placeholder="Ваш телефон"]').value;
    const debt = e.target.querySelector('input[placeholder="Сумма долга (тг)"]').value;
    const city = e.target.querySelector('input[placeholder="Ваш город"]').value;

    const message = `🚀 *Новая заявка с сайта!*\n\n` +
        `👤 Имя: ${name}\n` +
        `📞 Телефон: ${phone}\n` +
        `💰 Долг: ${debt} тг\n` +
        `📍 Город: ${city}`;

    btn.innerText = 'Отправка...';
    btn.disabled = true;

    try {
        const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: CHAT_ID,
                text: message,
                parse_mode: 'Markdown'
            })
        });

        if (response.ok) {
            alert('✅ Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.');
            e.target.reset();
        } else {
            throw new Error('Ошибка при отправке');
        }
    } catch (error) {
        alert('❌ Ошибка отправки. Пожалуйста, позвоните нам напрямую.');
        console.error(error);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
});
