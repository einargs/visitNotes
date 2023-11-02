import path from 'path'
import { defineConfig, searchForWorkspaceRoot } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: [{
      find: "@",
      replacement: path.resolve(__dirname, "./src"),
    },{
      find: "@recordings",
      replacement: path.resolve(__dirname, "./recordings")
    }],
  },
  server: {
    fs: {
      allow: [
        searchForWorkspaceRoot(process.cwd()),
        // We moved the ones we need to the recordings dir to make packaging
        // easier.
        // '../data/audio_recordings/'
      ],
    },
    proxy: {
      '/socket.io': {
        target: 'ws://[::1]:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
