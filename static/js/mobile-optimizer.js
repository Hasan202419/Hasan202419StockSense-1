/**
 * Mobile Optimization for 3D Trading Dashboard
 * Detects mobile devices and adjusts 3D performance accordingly
 */

class MobileOptimizer {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isTablet = this.detectTablet();
        this.deviceType = this.getDeviceType();
        this.performanceLevel = this.getPerformanceLevel();
    }

    /**
     * Detect if device is mobile
     */
    detectMobile() {
        return /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * Detect if device is tablet
     */
    detectTablet() {
        return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
    }

    /**
     * Get device type
     */
    getDeviceType() {
        if (this.isMobile) return 'mobile';
        if (this.isTablet) return 'tablet';
        return 'desktop';
    }

    /**
     * Determine performance level based on device
     * Returns: 'low', 'medium', 'high'
     */
    getPerformanceLevel() {
        // Check for specific indicators
        const gpuTier = this.estimateGPUTier();

        if (this.isMobile) {
            return 'low';
        } else if (this.isTablet) {
            return 'medium';
        } else if (gpuTier === 'high') {
            return 'high';
        } else {
            return 'medium';
        }
    }

    /**
     * Estimate GPU tier (simplified)
     */
    estimateGPUTier() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

        if (!gl) return 'low';

        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

            // High-end GPUs
            if (/RTX|Radeon RX|Apple M[1-9]|Mali-G/.test(renderer)) {
                return 'high';
            }
            // Low-end GPUs
            if (/Intel HD|Mali-4/.test(renderer)) {
                return 'low';
            }
        }

        return 'medium';
    }

    /**
     * Get optimized Three.js settings
     */
    getOptimizedSettings() {
        const settings = {
            antialias: true,
            shadowMap: true,
            fog: true,
            particleCount: 1000,
            textureQuality: 'high',
            maxLights: 5,
            renderScale: 1.0,
            animationFPS: 60
        };

        if (this.performanceLevel === 'low') {
            // Mobile optimization
            settings.antialias = false;
            settings.shadowMap = false;
            settings.fog = false;
            settings.particleCount = 200;
            settings.textureQuality = 'low';
            settings.maxLights = 2;
            settings.renderScale = 0.75;
            settings.animationFPS = 30;
        } else if (this.performanceLevel === 'medium') {
            // Tablet/mid-range optimization
            settings.antialias = true;
            settings.shadowMap = false;
            settings.fog = true;
            settings.particleCount = 500;
            settings.textureQuality = 'medium';
            settings.maxLights = 3;
            settings.renderScale = 0.9;
            settings.animationFPS = 45;
        }

        return settings;
    }

    /**
     * Apply optimizations to Three.js renderer
     */
    optimizeRenderer(renderer) {
        const settings = this.getOptimizedSettings();

        // Adjust pixel ratio
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, settings.renderScale * 2));

        // Shadow map settings
        if (settings.shadowMap) {
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        } else {
            renderer.shadowMap.enabled = false;
        }

        // Power preference
        if (this.performanceLevel === 'low') {
            renderer.powerPreference = 'low-power';
        }

        return renderer;
    }

    /**
     * Simplify geometry for low-end devices
     */
    simplifyGeometry(geometry, reductionFactor = 0.5) {
        if (this.performanceLevel === 'high') {
            return geometry;
        }

        // For low/medium performance, reduce geometry complexity
        if (geometry.type === 'SphereGeometry') {
            const segments = geometry.parameters.widthSegments;
            const newSegments = Math.max(8, Math.floor(segments * reductionFactor));
            return new THREE.SphereGeometry(
                geometry.parameters.radius,
                newSegments,
                newSegments
            );
        }

        if (geometry.type === 'CylinderGeometry') {
            const segments = geometry.parameters.radialSegments;
            const newSegments = Math.max(6, Math.floor(segments * reductionFactor));
            return new THREE.CylinderGeometry(
                geometry.parameters.radiusTop,
                geometry.parameters.radiusBottom,
                geometry.parameters.height,
                newSegments
            );
        }

        return geometry;
    }

    /**
     * Optimize material for mobile
     */
    optimizeMaterial(material) {
        if (this.performanceLevel === 'low') {
            // Replace expensive materials with basic ones
            if (material.type === 'MeshPhysicalMaterial') {
                const basicMaterial = new THREE.MeshLambertMaterial({
                    color: material.color,
                    transparent: material.transparent,
                    opacity: material.opacity
                });
                return basicMaterial;
            }
        }

        return material;
    }

    /**
     * Setup touch controls for mobile
     */
    setupTouchControls(controls, camera) {
        if (!this.isMobile && !this.isTablet) return;

        // Adjust control sensitivity for touch
        controls.rotateSpeed = 0.5;
        controls.zoomSpeed = 0.8;
        controls.panSpeed = 0.5;

        // Enable touch gestures
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;

        // Limit rotation range for mobile
        controls.minPolarAngle = Math.PI / 4;
        controls.maxPolarAngle = Math.PI / 2;

        // Add pinch-to-zoom support
        this.addPinchZoom(camera, controls);
    }

    /**
     * Add pinch-to-zoom functionality
     */
    addPinchZoom(camera, controls) {
        let initialDistance = 0;
        let currentDistance = 0;

        document.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                initialDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
                currentDistance = this.getTouchDistance(e.touches[0], e.touches[1]);
                const delta = currentDistance - initialDistance;

                // Adjust camera position
                const zoomFactor = 1 - (delta * 0.01);
                camera.position.multiplyScalar(zoomFactor);
                camera.position.clampLength(5, 30);

                initialDistance = currentDistance;
            }
        });
    }

    /**
     * Calculate distance between two touch points
     */
    getTouchDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Adjust UI layout for mobile
     */
    adjustUILayout() {
        if (!this.isMobile && !this.isTablet) return;

        // Hide or simplify complex UI elements
        const infoOverlay = document.getElementById('info-overlay');
        const sentimentPanel = document.getElementById('sentiment-panel');
        const controls = document.getElementById('controls');

        if (this.isMobile) {
            // Mobile: Compact layout
            if (infoOverlay) {
                infoOverlay.style.maxWidth = '90%';
                infoOverlay.style.fontSize = '12px';
                infoOverlay.style.padding = '10px';
            }

            if (sentimentPanel) {
                sentimentPanel.style.width = '90%';
                sentimentPanel.style.top = 'auto';
                sentimentPanel.style.bottom = '80px';
                sentimentPanel.style.left = '5%';
                sentimentPanel.style.right = '5%';
            }

            if (controls) {
                controls.style.flexWrap = 'wrap';
                controls.style.gap = '8px';
            }

            // Reduce button sizes
            const buttons = document.querySelectorAll('.control-btn');
            buttons.forEach(btn => {
                btn.style.padding = '8px 12px';
                btn.style.fontSize = '12px';
            });
        }
    }

    /**
     * Throttle animation frame rate
     */
    createThrottledAnimationLoop(callback) {
        const targetFPS = this.getOptimizedSettings().animationFPS;
        const interval = 1000 / targetFPS;
        let lastTime = 0;

        return function throttledAnimate(currentTime) {
            requestAnimationFrame(throttledAnimate);

            const delta = currentTime - lastTime;

            if (delta >= interval) {
                callback(currentTime);
                lastTime = currentTime - (delta % interval);
            }
        };
    }

    /**
     * Log device information
     */
    logDeviceInfo() {
        console.log('=== Mobile Optimizer ===');
        console.log('Device Type:', this.deviceType);
        console.log('Performance Level:', this.performanceLevel);
        console.log('Screen Size:', window.innerWidth + 'x' + window.innerHeight);
        console.log('Pixel Ratio:', window.devicePixelRatio);
        console.log('Settings:', this.getOptimizedSettings());
        console.log('========================');
    }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileOptimizer;
}
