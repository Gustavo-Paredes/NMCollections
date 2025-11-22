/**
 * WebSocket Alternative Client for Vercel Deployment
 * Uses Server-Sent Events instead of WebSockets
 */

class AuctionSSEClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.eventSource = null;
        this.auctionId = null;
        this.connectionId = null;
        this.onMessage = null;
        this.onError = null;
        this.onConnect = null;
        this.onDisconnect = null;
    }

    /**
     * Connect to auction updates via Server-Sent Events
     * @param {string} auctionId - The auction ID to connect to
     * @param {Object} callbacks - Event callbacks
     */
    connect(auctionId, callbacks = {}) {
        this.auctionId = auctionId;
        this.onMessage = callbacks.onMessage || (() => {});
        this.onError = callbacks.onError || (() => {});
        this.onConnect = callbacks.onConnect || (() => {});
        this.onDisconnect = callbacks.onDisconnect || (() => {});

        const url = `${this.baseUrl}/ws-alt/connect/${auctionId}`;
        this.eventSource = new EventSource(url);

        this.eventSource.addEventListener('connected', (event) => {
            const data = JSON.parse(event.data);
            this.connectionId = data.connection_id;
            console.log(`Connected to auction ${auctionId}, connection ID: ${this.connectionId}`);
            this.onConnect(data);
        });

        this.eventSource.addEventListener('auction_update', (event) => {
            const data = JSON.parse(event.data);
            console.log('Auction update received:', data);
            this.onMessage(data);
        });

        this.eventSource.addEventListener('heartbeat', (event) => {
            const data = JSON.parse(event.data);
            console.log('Heartbeat received at:', data.timestamp);
        });

        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.onError(error);
        };

        this.eventSource.onopen = () => {
            console.log('SSE connection opened');
        };
    }

    /**
     * Send data to the auction (for bidding, etc.)
     * @param {Object} data - Data to send
     */
    async send(data) {
        if (!this.auctionId) {
            throw new Error('Not connected to any auction');
        }

        try {
            const response = await fetch(`${this.baseUrl}/ws-alt/send/${this.auctionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            return await response.json();
        } catch (error) {
            console.error('Error sending data:', error);
            this.onError(error);
            throw error;
        }
    }

    /**
     * Get current auction status
     */
    async getStatus() {
        if (!this.auctionId) {
            throw new Error('Not connected to any auction');
        }

        try {
            const response = await fetch(`${this.baseUrl}/ws-alt/status/${this.auctionId}`);
            return await response.json();
        } catch (error) {
            console.error('Error getting status:', error);
            throw error;
        }
    }

    /**
     * Disconnect from the auction
     */
    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            console.log('Disconnected from auction');
            this.onDisconnect();
        }
        this.auctionId = null;
        this.connectionId = null;
    }

    /**
     * Check if currently connected
     */
    isConnected() {
        return this.eventSource && this.eventSource.readyState === EventSource.OPEN;
    }
}

// Usage example:
/*
const auctionClient = new AuctionSSEClient('/api');

auctionClient.connect('auction-123', {
    onConnect: (data) => {
        console.log('Connected to auction:', data);
    },
    onMessage: (data) => {
        console.log('New auction update:', data);
        // Update UI with new bid, auction state, etc.
    },
    onError: (error) => {
        console.error('Connection error:', error);
    },
    onDisconnect: () => {
        console.log('Disconnected from auction');
    }
});

// Send a bid
auctionClient.send({
    type: 'bid',
    amount: 150.00,
    user_id: 'user-456'
});

// Get auction status
auctionClient.getStatus().then(status => {
    console.log('Auction status:', status);
});

// Disconnect when done
auctionClient.disconnect();
*/

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuctionSSEClient;
}