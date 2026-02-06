'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to login page with signup mode
    // Since our login page handles both login and signup, we'll add a query param
    router.replace('/login?mode=signup');
  }, [router]);

  return null; // This component won't render anything since it redirects
}