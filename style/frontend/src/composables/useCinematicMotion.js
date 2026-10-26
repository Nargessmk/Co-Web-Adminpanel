import { nextTick } from 'vue'

let lenisInstance = null
let gsapTickerCallback = null
let scrollHandler = null
let retryTimer = null
let matchMediaInstance = null

export function useCinematicMotion () {
  function initMotion () {
    nextTick(() => {
      if (typeof window === 'undefined') return

      let attempts = 0
      const maxAttempts = 30

      function startMotionSequence () {
        const Lenis = window.Lenis
        const gsap = window.gsap
        const ScrollTrigger = window.ScrollTrigger

        if ((!gsap || !Lenis) && attempts < maxAttempts) {
          attempts++
          retryTimer = setTimeout(startMotionSequence, 50)
          return
        }

        document.documentElement.classList.add('has-motion')
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

        // 1. Initialize Lenis Smooth Scroll
        if (!reduceMotion && Lenis) {
          if (lenisInstance) {
            try { lenisInstance.destroy() } catch (_) {}
          }

          lenisInstance = new Lenis({
            lerp: 0.08,
            smoothWheel: true,
            wheelMultiplier: 0.95,
          })

          if (ScrollTrigger) {
            lenisInstance.on('scroll', ScrollTrigger.update)
          }

          if (gsap) {
            if (gsapTickerCallback) {
              gsap.ticker.remove(gsapTickerCallback)
            }
            gsapTickerCallback = (time) => {
              if (lenisInstance) lenisInstance.raf(time * 1000)
            }
            gsap.ticker.add(gsapTickerCallback)
            gsap.ticker.lagSmoothing(0)
          }
        }

        // Smooth anchor scrolling
        document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
          anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href')
            if (targetId && targetId !== '#') {
              const targetElement = document.querySelector(targetId)
              if (targetElement) {
                e.preventDefault()
                if (lenisInstance) {
                  lenisInstance.scrollTo(targetElement, { offset: -30, duration: 1.15 })
                } else {
                  targetElement.scrollIntoView({ behavior: 'smooth' })
                }
              }
            }
          })
        })

        // 2. Cinematic GSAP Motion System
        if (gsap) {
          if (ScrollTrigger) {
            gsap.registerPlugin(ScrollTrigger)
          }

          gsap.defaults({ ease: 'power3.out', duration: 0.85 })

          if (!reduceMotion) {
            // (A) Hero Section Majestic Page-Load Timeline
            const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } })

            const floatingHeader = document.querySelector('.floating-header')
            const heroDashboard = document.querySelector('.hero-dashboard-frame')
            const heroTag = document.querySelector('.hero-tag-badge')
            const heroHeading = document.querySelector('.hero-heading')
            const heroSubtext = document.querySelector('.hero-subtext')
            const heroButtons = document.querySelectorAll('.hero-actions-group .btn-pill')
            const heroMetrics = document.querySelector('.hero-metrics-strip')

            if (floatingHeader) {
              heroTl.fromTo(
                floatingHeader,
                { y: -25, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.9, clearProps: 'y,opacity' }
              )
            }
            if (heroDashboard) {
              heroTl.fromTo(
                heroDashboard,
                { y: 35, opacity: 0, scale: 0.97 },
                { y: 0, opacity: 1, scale: 1, duration: 1 },
                '-=0.5'
              )
            }
            if (heroTag) {
              heroTl.fromTo(
                heroTag,
                { y: 18, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.75 },
                '-=0.65'
              )
            }
            if (heroHeading) {
              heroTl.fromTo(
                heroHeading,
                { y: 28, opacity: 0, filter: 'blur(8px)' },
                { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.95 },
                '-=0.55'
              )
            }
            if (heroSubtext) {
              heroTl.fromTo(
                heroSubtext,
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8 },
                '-=0.6'
              )
            }
            if (heroButtons.length) {
              heroTl.fromTo(
                heroButtons,
                { y: 16, opacity: 0 },
                { y: 0, opacity: 1, stagger: 0.1, duration: 0.7 },
                '-=0.55'
              )
            }
            if (heroMetrics) {
              heroTl.fromTo(
                heroMetrics,
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.8 },
                '-=0.45'
              )
            }

            // (B) SECTION 2 LAYER CURTAIN OVERLAY MOTION
            const heroSection = document.getElementById('sec-hero')
            const servicesSection = document.getElementById('sec-services')

            if (heroSection && servicesSection && ScrollTrigger) {
              ScrollTrigger.create({
                trigger: heroSection,
                start: 'top top',
                endTrigger: servicesSection,
                end: 'top top',
                pin: true,
                pinSpacing: false,
              })

              const heroContainer = heroSection.querySelector('.hero-container') || heroSection.querySelector('.container')
              if (heroContainer) {
                gsap.to(heroContainer, {
                  y: -40,
                  scale: 0.96,
                  opacity: 0.75,
                  ease: 'none',
                  scrollTrigger: {
                    trigger: servicesSection,
                    start: 'top bottom',
                    end: 'top top',
                    scrub: true,
                  },
                })
              }

              gsap.fromTo(
                servicesSection,
                {
                  borderTopLeftRadius: 56,
                  borderTopRightRadius: 56,
                },
                {
                  borderTopLeftRadius: 0,
                  borderTopRightRadius: 0,
                  ease: 'none',
                  scrollTrigger: {
                    trigger: servicesSection,
                    start: 'top 50%',
                    end: 'top top',
                    scrub: true,
                  },
                }
              )
            }

            // (C) Section Headers Elegant Blur-Up Reveal
            if (ScrollTrigger) {
              gsap.utils.toArray('.section-head').forEach((elem) => {
                const tag = elem.querySelector('.section-tag')
                const title = elem.querySelector('.section-title')
                const desc = elem.querySelector('.section-desc')

                const tl = gsap.timeline({
                  scrollTrigger: {
                    trigger: elem,
                    start: 'top 88%',
                    once: true,
                  },
                })

                if (tag) tl.fromTo(tag, { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7 })
                if (title) tl.fromTo(title, { y: 22, opacity: 0, filter: 'blur(6px)' }, { y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.85 }, '-=0.5')
                if (desc) tl.fromTo(desc, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.75 }, '-=0.55')
              })
            }

            // (D) Services Cards Staggered Entry
            const servicesGrid = document.querySelector('.services-grid')
            if (servicesGrid && ScrollTrigger) {
              const cards = servicesGrid.querySelectorAll('.service-card')
              gsap.fromTo(
                cards,
                { y: 36, opacity: 0, scale: 0.98 },
                {
                  y: 0,
                  opacity: 1,
                  scale: 1,
                  duration: 0.85,
                  stagger: 0.08,
                  ease: 'power3.out',
                  scrollTrigger: {
                    trigger: servicesGrid,
                    start: 'top 86%',
                    once: true,
                  },
                }
              )
            }

            // (E) Projects Showcase Items Sequential Reveal & Parallax
            if (ScrollTrigger) {
              gsap.utils.toArray('.project-showcase-item').forEach((item) => {
                gsap.fromTo(
                  item,
                  { y: 44, opacity: 0 },
                  {
                    y: 0,
                    opacity: 1,
                    duration: 0.95,
                    ease: 'power3.out',
                    scrollTrigger: {
                      trigger: item,
                      start: 'top 84%',
                      once: true,
                    },
                  }
                )

                const img = item.querySelector('.project-media-frame img')
                if (img) {
                  gsap.fromTo(
                    img,
                    { yPercent: -4 },
                    {
                      yPercent: 4,
                      ease: 'none',
                      scrollTrigger: {
                        trigger: item,
                        start: 'top bottom',
                        end: 'bottom top',
                        scrub: 1.2,
                      },
                    }
                  )
                }
              })
            }

            // (F) About Section Unified Single Card Reveal
            const aboutCard = document.querySelector('.about-single-card')
            if (aboutCard && ScrollTrigger) {
              gsap.fromTo(
                aboutCard,
                { y: 36, opacity: 0 },
                {
                  y: 0,
                  opacity: 1,
                  duration: 0.95,
                  ease: 'power3.out',
                  scrollTrigger: {
                    trigger: aboutCard,
                    start: 'top 86%',
                    once: true,
                  },
                }
              )

              const featureItems = aboutCard.querySelectorAll('.feature-item')
              if (featureItems.length > 0) {
                gsap.fromTo(
                  featureItems,
                  { x: 20, opacity: 0 },
                  {
                    x: 0,
                    opacity: 1,
                    duration: 0.75,
                    stagger: 0.08,
                    ease: 'power3.out',
                    scrollTrigger: {
                      trigger: aboutCard,
                      start: 'top 82%',
                      once: true,
                    },
                  }
                )
              }
            }

            // (G) Articles Cards Stagger
            const articlesGrid = document.querySelector('.articles-grid')
            if (articlesGrid && ScrollTrigger) {
              const articles = articlesGrid.querySelectorAll('.article-card')
              gsap.fromTo(
                articles,
                { y: 36, opacity: 0 },
                {
                  y: 0,
                  opacity: 1,
                  duration: 0.85,
                  stagger: 0.1,
                  ease: 'power3.out',
                  scrollTrigger: {
                    trigger: articlesGrid,
                    start: 'top 86%',
                    once: true,
                  },
                }
              )
            }

            // (H) Contact Bento Card Reveal
            const contactCard = document.querySelector('.contact-bento-card')
            if (contactCard && ScrollTrigger) {
              gsap.fromTo(
                contactCard,
                { y: 40, opacity: 0 },
                {
                  y: 0,
                  opacity: 1,
                  duration: 0.95,
                  ease: 'power3.out',
                  scrollTrigger: {
                    trigger: contactCard,
                    start: 'top 86%',
                    once: true,
                  },
                }
              )
            }

            // (I) Active Nav Link Tracking on Scroll
            const sections = document.querySelectorAll('section[id]')
            const navLinks = document.querySelectorAll('.nav-links a, .mobile-nav-links a')

            if (scrollHandler) {
              window.removeEventListener('scroll', scrollHandler)
            }

            scrollHandler = () => {
              let current = ''
              sections.forEach((section) => {
                const sectionTop = section.offsetTop - 140
                if (window.scrollY >= sectionTop) {
                  current = section.getAttribute('id')
                }
              })

              navLinks.forEach((link) => {
                link.classList.remove('active')
                if (link.getAttribute('href') === '#' + current) {
                  link.classList.add('active')
                }
              })
            }

            window.addEventListener('scroll', scrollHandler, { passive: true })

            // Refresh ScrollTrigger after elements, fonts, and images render
            if (ScrollTrigger) {
              if (document.fonts?.ready) {
                document.fonts.ready.then(() => {
                  ScrollTrigger.refresh()
                })
              }
              window.addEventListener('load', () => ScrollTrigger.refresh(), { once: true })
              setTimeout(() => ScrollTrigger.refresh(), 250)
              setTimeout(() => ScrollTrigger.refresh(), 650)
            }
          }
        } else {
          // Fallback: Reveal all immediately
          document.querySelectorAll('.motion-reveal, .motion-stagger-item').forEach((el) => {
            el.style.opacity = '1'
            el.style.transform = 'none'
          })
        }
      }

      startMotionSequence()
    })
  }

  function destroyMotion () {
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }

    if (typeof window !== 'undefined') {
      if (scrollHandler) {
        window.removeEventListener('scroll', scrollHandler)
        scrollHandler = null
      }

      const gsap = window.gsap
      const ScrollTrigger = window.ScrollTrigger
      if (ScrollTrigger) {
        try {
          ScrollTrigger.getAll().forEach((t) => t.kill())
        } catch (_) {}
      }
      if (gsap && gsapTickerCallback) {
        try {
          gsap.ticker.remove(gsapTickerCallback)
        } catch (_) {}
        gsapTickerCallback = null
      }
      if (matchMediaInstance) {
        try {
          matchMediaInstance.revert()
        } catch (_) {}
        matchMediaInstance = null
      }
      if (lenisInstance) {
        try {
          lenisInstance.destroy()
        } catch (_) {}
        lenisInstance = null
      }
    }
  }

  function stopLenis () {
    if (lenisInstance) {
      try {
        lenisInstance.stop()
      } catch (_) {}
    }
  }

  function startLenis () {
    if (lenisInstance) {
      try {
        lenisInstance.start()
      } catch (_) {}
    }
  }

  return {
    initMotion,
    destroyMotion,
    stopLenis,
    startLenis,
  }
}
