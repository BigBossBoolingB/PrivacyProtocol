const CACHE_NAME = 'base44-app-cache-v1';
// These URLs would ideally be dynamically generated from Vite's build manifest
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  // Assuming Vite output structure, these will have hashes in reality
  // For now, using generic paths. This part will need adjustment after a real build.
  '/assets/index.css', // Placeholder for actual CSS file
  '/assets/main.js',   // Placeholder for actual JS entry file
  '/assets/vendor.js', // Placeholder for actual vendor chunk
  '/manifest.webmanifest' // The web app manifest
  // Add other critical assets like logo, key fonts if locally hosted
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(PRECACHE_ASSETS.map(url => new Request(url, { cache: 'reload' }))); // Force reload for precaching
      })
      .then(() => {
        console.log('All specified assets have been cached.');
        self.skipWaiting(); // Activate the new service worker immediately
      })
      .catch(error => {
        console.error('Failed to cache assets during install:', error);
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service worker activated and old caches cleaned.');
      return self.clients.claim(); // Take control of uncontrolled clients
    })
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return; // Only handle GET requests
  }

  const url = new URL(event.request.url);

  // Strategy 1: Navigation requests (e.g., loading the main HTML)
  // Network first, then cache fallback for the main app page.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            // If network fails or returns an error, try the cache for index.html
            return caches.match('/index.html').then(cachedResponse => {
              return cachedResponse || response; // Return original error response if not in cache
            });
          }
          return response; // Return network response
        })
        .catch(() => {
          // Network totally failed, try cache for index.html
          return caches.match('/index.html');
        })
    );
    return;
  }

  // Strategy 2: API GET requests (Network first, then cache)
  // IMPORTANT: Adjust the condition to accurately match your API GET requests.
  // This example assumes API requests might go to a different origin or have a specific path.
  // For Base44 SDK, this might be more complex if it calls various external domains.
  // A more robust solution would involve inspecting headers or using a more specific URL pattern.
  if (url.pathname.startsWith('/api/') || event.request.url.includes('api.base44.com')) { // Example condition
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          // If successful, cache the response and return it
          if (networkResponse && networkResponse.ok) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          console.log('Network fetch failed for API, trying cache:', event.request.url);
          return caches.match(event.request);
        })
    );
    return;
  }

  // Strategy 3: Static assets (Cache first, then network)
  // This primarily serves assets from the precache.
  // If an asset isn't in precache (e.g. lazy loaded images not part of initial bundle),
  // it will be fetched and could be cached here dynamically if desired.
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse; // Serve from cache
        }
        // Not in cache, fetch from network
        return fetch(event.request).then((networkResponse) => {
          // Optionally, cache newly fetched static assets dynamically if they weren't precached.
          // For now, we rely on precache for static assets.
          return networkResponse;
        });
      })
      // No specific catch here, as network failure for a non-cached, non-API static asset
      // would typically result in a browser error anyway.
  );
});
