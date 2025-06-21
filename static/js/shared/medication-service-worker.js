// static/js/medication-service-worker.js
const CACHE_NAME = 'medication-reminder-cache-v1';
const FILES_TO_CACHE = [
    '/static/images/alerta.png',
    '/static/sounds/alert.mp3'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return Promise.all(
                    FILES_TO_CACHE.map(url => {
                        return fetch(url, {cache: 'no-cache'})
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error(`Failed to fetch ${url}: ${response.status}`);
                                }
                                return cache.put(url, response);
                            })
                            .catch(err => {
                                console.error('Failed to cache:', url, err);
                            });
                    })
                );
            })
    );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            }));
        })
    );
    self.clients.claim();
});

// Manejo de mensajes desde la página
self.addEventListener('message', (event) => {
    if (event.data.type === 'SHOW_NOTIFICATION') {
        const { title, body } = event.data.notification;
        event.waitUntil(
            self.registration.showNotification(title, {
                body,
                icon: '/static/images/alerta.png',
                vibrate: [200, 100, 200]
            })
        );
    }
});

// Manejo de clics en notificaciones
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({type: 'window'})
            .then((clientList) => {
                const urlToOpen = new URL('/paciente/medicamentos', self.location.origin).href;
                
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                return clients.openWindow(urlToOpen);
            })
    );
});