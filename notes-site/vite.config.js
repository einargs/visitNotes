import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [{
      find: "@",
      replacement: path.resolve(__dirname, "./src"),
    }],
  },
  server: {
    proxy: {
      /* This isn't working, I think because it refuses to proxy both http long
         polling, which it always does at the start before upgrading, and
         websockets. */
      '/socket.io': {
        target: 'ws://[::1]:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
