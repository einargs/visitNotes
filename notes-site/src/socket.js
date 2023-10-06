import { io } from 'socket.io-client';

const URL = "localhost:5000";

export const socket = io(URL);

// Currently just sends an empty event, because we have no audio.
export function sendAudio(handler) {
  socket.timeout(5000).emit('audio', handler)
}
