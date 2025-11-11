// Animations for Home page
document.addEventListener('DOMContentLoaded', function() {
    // Add parallax effect to hero section
    const hero = document.querySelector('hero');
    if (hero) {
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            const moveX = (x - 0.5) * 20;
            const moveY = (y - 0.5) * 20;
            
            hero.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
    }

    // Animate arena cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, observerOptions);

    // Observe arena cards
    document.querySelectorAll('.arena-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Observe reason cards
    document.querySelectorAll('.reason-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Add floating animation to hero button
    const heroButton = document.querySelector('hero > button');
    if (heroButton) {
        setInterval(() => {
            heroButton.style.transform = 'translate(-50%, -50%) translateY(-5px)';
            setTimeout(() => {
                heroButton.style.transform = 'translate(-50%, -50%) translateY(0)';
            }, 1000);
        }, 2000);
    }

    // Add glow pulse to h2 headings
    const h2Elements = document.querySelectorAll('h2');
    h2Elements.forEach(h2 => {
        setInterval(() => {
            h2.style.filter = 'drop-shadow(0 0 12px #FFA200)';
            setTimeout(() => {
                h2.style.filter = 'drop-shadow(0 0 8px #FFA200)';
            }, 1000);
        }, 2000);
    });
});

