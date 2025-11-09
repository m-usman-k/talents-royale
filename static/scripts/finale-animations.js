// Create golden particles for Finale Royale
document.addEventListener('DOMContentLoaded', function() {
    // Create particles container
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'gold-particles';
    document.querySelector('.finale-section').prepend(particlesContainer);

    // Create particles
    function createParticles() {
        const particleCount = 30;
        const colors = ['#FFD700', '#FFA500', '#FFD700', '#FFC000', '#FFD700'];
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'gold-particle';
            
            // Random size between 2px and 8px
            const size = Math.random() * 6 + 2;
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random animation duration between 15s and 40s
            const duration = Math.random() * 25 + 15;
            
            // Random delay up to 20s
            const delay = Math.random() * 20;
            
            // Random color from gold palette
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            // Random shape (circle or square)
            const isCircle = Math.random() > 0.5;
            
            // Apply styles
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.background = color;
            particle.style.boxShadow = `0 0 ${size * 3}px ${size}px ${color}`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `-${delay}s`;
            particle.style.borderRadius = isCircle ? '50%' : '2px';
            particle.style.opacity = '0.7';
            
            // Add to container
            particlesContainer.appendChild(particle);
        }
    }

    // Initialize particles
    createParticles();

    // Add parallax effect to background
    const finaleSection = document.querySelector('.finale-section');
    if (finaleSection) {
        document.addEventListener('mousemove', function(e) {
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            // Subtle parallax effect
            const moveX = (x - 0.5) * 30;
            const moveY = (y - 0.5) * 30;
            
            finaleSection.style.backgroundPosition = 
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

    // Add gold shimmer to text
    const addShimmer = (element) => {
        if (!element) return;
        
        const text = element.textContent;
        element.innerHTML = '';
        
        text.split('').forEach((char, i) => {
            const span = document.createElement('span');
            span.textContent = char;
            span.style.animationDelay = `${i * 0.05}s`;
            element.appendChild(span);
        });
    };

    // Apply shimmer to main title
    const mainTitle = document.querySelector('.finale-section h1');
    if (mainTitle) {
        mainTitle.style.background = 'linear-gradient(45deg, #FFD700, #FFA500, #FFD700, #FFC000)';
        mainTitle.style.backgroundSize = '300% 300%';
        mainTitle.style.webkitBackgroundClip = 'text';
        mainTitle.style.webkitTextFillColor = 'transparent';
        mainTitle.style.animation = 'shimmer 3s linear infinite';
        addShimmer(mainTitle);
    }

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatGold {
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
        
        .gold-particles {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            overflow: hidden;
        }
        
        .gold-particle {
            position: absolute;
            animation: floatGold linear infinite;
            pointer-events: none;
            will-change: transform, opacity;
        }
        
        .finale-section h1 span {
            display: inline-block;
            animation: floatUp 1s ease-in-out infinite alternate;
            animation-delay: inherit;
        }
        
        @keyframes floatUp {
            0% {
                transform: translateY(0);
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
            }
            100% {
                transform: translateY(-5px);
                text-shadow: 0 0 20px rgba(255, 215, 0, 1);
            }
        }
    `;
    document.head.appendChild(style);
});
