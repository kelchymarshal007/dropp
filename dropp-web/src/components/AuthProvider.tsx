'use client';
import { GoogleOAuthProvider } from '@react-oauth/google';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <GoogleOAuthProvider clientId="923686141067-utfodb3otgm6kjhpoh8adds8jaoju96r.apps.googleusercontent.com">
      {children}
    </GoogleOAuthProvider>
  );
}
