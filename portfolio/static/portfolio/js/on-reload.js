import { annotate, annotationGroup  } from './rough-notation.esm.js';

let blueClear = 'rgba(45, 212, 191, 0.25)';
let lighterBlue = '#2dd4bf';
let annotationGroupInstance = null;

let lightmode = localStorage.getItem('lightmode')
const themeSwitch = document.getElementById('theme-switch')

// Runs when lightmode is enabled
const enableLightmode = () => {
    document.body.classList.add('lightmode')
    localStorage.setItem('lightmode', 'active')
    blueClear = 'rgba(13, 148, 136, 0.15)';
    lighterBlue = '#0d9488';
}

// Runs when lightmode is disabled
const disableLightmode = () => {
    document.body.classList.remove('lightmode')
    localStorage.setItem('lightmode', null)
    blueClear = 'rgba(45, 212, 191, 0.25)';
    lighterBlue = '#2dd4bf';
}

// Checks memory if lightmode was active last
if(lightmode === "active") enableLightmode()

const navLinks = Array.from(document.querySelectorAll('.navbar a[href^="#"]'));
const sections = navLinks
    .map(link => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

const setActiveNavLink = (sectionId) => {
    navLinks.forEach(link => {
        const isActive = link.getAttribute('href') === `#${sectionId}`;
        link.classList.toggle('active', isActive);

        if (isActive) {
            link.setAttribute('aria-current', 'page');
        } else {
            link.removeAttribute('aria-current');
        }
    });
};

if (sections.length > 0) {
    setActiveNavLink(sections[0].id);

    const sectionObserver = new IntersectionObserver((entries) => {
        const visibleSection = entries
            .filter(entry => entry.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visibleSection) {
            setActiveNavLink(visibleSection.target.id);
        }
    }, {
        rootMargin: '-28% 0px -55% 0px',
        threshold: [0, 0.2, 0.5],
    });

    sections.forEach(section => sectionObserver.observe(section));
}

navLinks.forEach(link => {
    link.addEventListener('click', () => {
        const sidebarToggle = document.getElementById('sidebar-active');
        if (sidebarToggle) sidebarToggle.checked = false;
    });
});

// When my lightmode/darkmode button is clicked...
themeSwitch.addEventListener("click", () => {
    document.body.classList.add('theme-transitioning');
    lightmode = localStorage.getItem('lightmode')
    lightmode !== "active" ? enableLightmode() : disableLightmode()
    removeAnnotations();
    roughNotionFunction();

    window.setTimeout(() => {
        document.body.classList.remove('theme-transitioning');
    }, 700);
})

// My Rough Notation handler
function roughNotionFunction() {
    removeAnnotations();

    // Define variables
    const textAnnotations = [];
    const title = document.querySelector('.highlight');
    const elements = document.querySelectorAll('.about-me span');

    // Safety: Check if elements exist before trying to map them
    if (elements.length > 0) {
        elements.forEach(element => {
            const annotation = annotate(element, { 
                type: 'highlight', 
                color: blueClear,
                iterations: 1,
            });
            textAnnotations.push(annotation);
        });
    }

    // Combine annotations (only include title if it exists)
    let allAnnotations = [...textAnnotations];
    
    if (title) {
        const a1 = annotate(title, { 
            type: 'underline', 
            color: lighterBlue, 
            padding: 0
        });
        allAnnotations = [a1, ...allAnnotations];
    }

    // Show the annotation group
    if (allAnnotations.length > 0) {
        annotationGroupInstance = annotationGroup(allAnnotations);
        annotationGroupInstance.show(); 
    }
}
// Expose to window so your API calls can trigger it
window.roughNotionFunction = roughNotionFunction;

// Checks if there are any current active annotations
function removeAnnotations() {
    if (annotationGroupInstance) {
        annotationGroupInstance.hide();
        annotationGroupInstance = null;
    }

    const existingSVGs = document.querySelectorAll('svg.rough-annotation');
    existingSVGs.forEach(svg => {
        svg.remove();
    });
}

// REMOVED FILTERING FUNCTION IN CURRENT ITERATION
// Controls the filter buttons on my projects section
// function projectsFunction() {
//     const iso = new Isotope('.projects-grid');
//     const filterButtons = Array.prototype.slice.call(document.querySelectorAll('.filter-button'));

//     filterButtons.map(button => {
//         button.addEventListener('click', function() {
//         filterButtons.map(button => button.classList.remove('active-filter'));
//         const type = this.getAttribute('data-filter');
//         this.classList.add('active-filter');
//         iso.arrange({
//             // item element provided as argument
//             filter: type && `.${type}`
//         });
//         iso.layout();
//         });
//     });
// }

// window.addEventListener('load', () => {
//     projectsFunction();
// })
