// Animations for Contestants page
document.addEventListener('DOMContentLoaded', function() {
    // Add parallax effect to background
    const mainContestants = document.querySelector('.main-contestants');
    if (mainContestants) {
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            const moveX = (x - 0.5) * 30;
            const moveY = (y - 0.5) * 30;
            
            mainContestants.style.backgroundPosition = 
                `calc(50% + ${moveX}px) calc(50% + ${moveY}px)`;
        });
    }

    // Animate contestant cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) scale(1)';
                }, index * 100);
            }
        });
    }, observerOptions);

    // Observe top contestant cards
    document.querySelectorAll('.top-contestants .contestant-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px) scale(0.9)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        observer.observe(card);
    });

    // Observe rank items
    document.querySelectorAll('.rank-item').forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-30px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });

    // Add pulsing effect to champion badge
    const championBadge = document.querySelector('.champion-badge');
    if (championBadge) {
        setInterval(() => {
            championBadge.style.transform = 'translateX(-50%) scale(1.1)';
            championBadge.style.boxShadow = '0 0 15px rgba(255, 162, 0, 1)';
            setTimeout(() => {
                championBadge.style.transform = 'translateX(-50%) scale(1)';
                championBadge.style.boxShadow = '0 0 10px rgba(255, 162, 0, 0.8)';
            }, 1000);
        }, 2000);
    }

    // Add glow pulse to logo text
    const logoText = document.querySelector('.logo-text');
    if (logoText) {
        setInterval(() => {
            logoText.style.filter = 'drop-shadow(0 0 12px #FF00F6)';
            setTimeout(() => {
                logoText.style.filter = 'drop-shadow(0 0 8px #FF00F6)';
            }, 1000);
        }, 2000);
    });

    // Add number counter animation to votes
    document.querySelectorAll('.votes').forEach(voteElement => {
        const text = voteElement.textContent;
        const match = text.match(/([\d,]+)/);
        if (match) {
            const number = parseFloat(match[1].replace(/,/g, ''));
            let current = 0;
            const increment = number / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= number) {
                    current = number;
                    clearInterval(timer);
                }
                voteElement.textContent = text.replace(match[1], Math.floor(current).toLocaleString());
            }, 30);
        }
    });
});

