import { type JSX } from 'react';
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { signUp } from '@/lib/auth-api';
import { useToast } from '#/context/ToastMessage.tsx';
import { currentUserQueryKey } from '@/lib/auth-api';

export function RegistrationModal({
  isVisible,
  onClose,
}: {
  isVisible: boolean;
  onClose: () => void;
}): JSX.Element {
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const signUpMutation = useMutation({
    mutationFn: () => signUp(email, password),
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user);
      setPassword('');

      // TODO: User should have opportunity to enter f_name and l_name, to show user name in ToastMessage
      addToast(`Account created successfully!`, 'Success');
      onClose();
    },
    onError: (error) => {
      addToast(error.message, 'Error');
    },
  });

  return (
    <div
      className={`fixed inset-0 z-40 items-center justify-center bg-black/30 backdrop-blur-sm ${isVisible ? 'flex' : 'hidden'}`}
    >
      <div className="relative rounded-xl border border-[var(--line)] bg-[var(--foam)]">
        <button
          aria-label="Close registration form"
          className="cursor-pointer absolute right-2 top-2"
          onClick={onClose}
          type="button"
        >
          X
        </button>
        <form
          id="registration-form"
          name="registration"
          className="flex flex-col items-center gap-4 p-20"
          onSubmit={(event) => {
            event.preventDefault();
            signUpMutation.mutate();
          }}
        >
          <h2 className="text-3xl">Registration</h2>
          <div className="flex flex-col">
            <label htmlFor="registration-email">Email</label>
            <input
              id="registration-email"
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Email"
              required
            />
          </div>
          <div className="flex w-full flex-col">
            <label htmlFor="registration-password">Password</label>
            <input
              id="registration-password"
              className="w-full rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              required
            />
          </div>
          <button
            aria-label="Create account"
            type="submit"
            className="mt-[25px] cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 text-sm font-semibold text-white"
            disabled={signUpMutation.isPending}
          >
            {signUpMutation.isPending ? '...' : 'Sign Up'}
          </button>
        </form>
      </div>
    </div>
  );
}
