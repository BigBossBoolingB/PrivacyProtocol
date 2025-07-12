const CACHE_NAME = 'privacy-protocol-v1';
const STATIC_CACHE_NAME = 'privacy-protocol-static-v1';
const API_CACHE_NAME = 'privacy-protocol-api-v1';

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/js/bundle.js',
  '/static/css/main.css'
];

const API_ENDPOINTS = [
  '/api/policy-monitor',
  '/api/risk-score-calculator',
  '/api/subscription-manager'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      }),
      caches.open(API_CACHE_NAME)
    ])
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE_NAME && 
              cacheName !== API_CACHE_NAME && 
              cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') {
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
  } else if (STATIC_ASSETS.some(asset => url.pathname.endsWith(asset))) {
    event.respondWith(handleStaticAsset(request));
  } else {
    event.respondWith(handleNavigationRequest(request));
  }
});

async function handleStaticAsset(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Failed to fetch static asset:', error);
    return new Response('Offline', { status: 503 });
  }
}

async function handleApiRequest(request) {
  const cache = await caches.open(API_CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return networkResponse;
  } catch (error) {
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response(
      JSON.stringify({ error: 'Offline - cached data not available' }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

async function handleNavigationRequest(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match('/index.html');
    return cachedResponse || new Response('Offline', { status: 503 });
  }
}

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
