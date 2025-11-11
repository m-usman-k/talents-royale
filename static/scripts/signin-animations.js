// Create floating particles for Signin page
document.addEventListener('DOMContentLoaded', function() {
    // Create particles container
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'signin-particles';
    document.querySelector('.signin-hero').appendChild(particlesContainer);

    // Create particles
    function createParticles() {
        const particleCount = 40;
        const colors = ['#00E5FF', '#F100F7', '#FFA200', '#FFD700'];
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'signin-particle';
            
            // Random size between 2px and 6px
            const size = Math.random() * 4 + 2;
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random animation duration between 10s and 30s
            const duration = Math.random() * 20 + 10;
            
            // Random delay up to 15s
            const delay = Math.random() * 15;
            
            // Random color
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            // Apply styles
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.background = color;
            particle.style.boxShadow = `0 0 ${size * 2}px ${size}px ${color}`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `-${delay}s`;
            
            // Add to container
            particlesContainer.appendChild(particle);
        }
    }

    // Initialize particles
    createParticles();

    // Add parallax effect to background
    const signinHero = document.querySelector('.signin-hero');
    if (signinHero) {
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            const moveX = (x - 0.5) * 30;
            const moveY = (y - 0.5) * 30;
            
            signinHero.style.backgroundPosition = 
                `calc(50% + ${moveX}px) calc(50% + ${moveY}px)`;
        });
    }

    // Add pulsing effect to the crown
    const crown = document.querySelector('.crown-icon img');
    if (crown) {
        setInterval(() => {
            crown.style.transform = 'scale(1.1)';
            setTimeout(() => {
                crown.style.transform = 'scale(1)';
            }, 1000);
        }, 2000);
    }

    // Add shimmer to title
    const title = document.querySelector('.signin-content h1');
    if (title) {
        title.style.background = 'linear-gradient(45deg, #FFA200, #FFD700, #00E5FF, #F100F7, #FFA200)';
        title.style.backgroundSize = '300% 300%';
        title.style.webkitBackgroundClip = 'text';
        title.style.webkitTextFillColor = 'transparent';
        title.style.animation = 'shimmer 3s linear infinite';
    }

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatSignin {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 0.7;
            }
            90% {
                opacity: 0.7;
            }
            100% {
                transform: translateY(-1000px) rotate(720deg);
                opacity: 0;
            }
        }
        
        @keyframes shimmer {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        
        .signin-particles {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        
        .signin-particle {
            position: absolute;
            animation: floatSignin linear infinite;
            pointer-events: none;
            will-change: transform, opacity;
            border-radius: 50%;
        }
    `;
    document.head.appendChild(style);
});

