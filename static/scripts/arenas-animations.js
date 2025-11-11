// Animations for Arenas page
document.addEventListener('DOMContentLoaded', function() {
    // Add parallax effect to background
    const mainArena = document.querySelector('.main-arena');
    if (mainArena) {
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            const moveX = (x - 0.5) * 30;
            const moveY = (y - 0.5) * 30;
            
            mainArena.style.backgroundPosition = 
                `calc(50% + ${moveX}px) calc(50% + ${moveY}px)`;
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
                    entry.target.style.transform = 'translateY(0) scale(1)';
                }, index * 150);
            }
        });
    }, observerOptions);

    // Observe arena cards
    document.querySelectorAll('.each-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px) scale(0.9)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        observer.observe(card);
    });

    // Observe tier cards
    document.querySelectorAll('.tier-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-50px)';
        card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        observer.observe(card);
    });

    // Add glow pulse to headings
    const h2Elements = document.querySelectorAll('h2');
    h2Elements.forEach(h2 => {
        setInterval(() => {
            h2.style.filter = 'drop-shadow(0 0 12px #FFA200)';
            setTimeout(() => {
                h2.style.filter = 'drop-shadow(0 0 8px #FFA200)';
            }, 1000);
        }, 2000);
    });

    // Add hover glow effect to buttons
    document.querySelectorAll('.each-card button, .tier-card button').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 20px rgba(0, 229, 255, 0.8), 0 0 30px rgba(255, 0, 246, 0.6)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.boxShadow = '';
        });
    });
});

