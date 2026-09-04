import { useMutation, useQueryClient } from '@tanstack/react-query';
import { type JSX, useId, useState } from 'react';
import { useToast } from '#/context/toast-context.ts';
import { currentUserQueryKey, signUp } from '@/lib/auth-api';

export function RegistrationModal({
  isRegistrationFormVisible,
  onClose,
}: {
  isRegistrationFormVisible: boolean;
  onClose: () => void;
}): JSX.Element {
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const uid = useId();
  const formId = `${uid}-form`;
  const emailId = `${uid}-email`;
  const passwordId = `${uid}-password`;

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
      className={`fixed inset-0 z-40 items-center justify-center bg-black/30 backdrop-blur-sm ${isRegistrationFormVisible ? 'flex' : 'hidden'}`}
    >
      <div className="relative rounded-xl border border-[var(--line)] bg-[var(--foam)]">
        <button
          aria-label="Close registration form"
          className="absolute top-2 right-2 cursor-pointer"
          onClick={onClose}
          type="button"
        >
          X
        </button>
        <form
          id={formId}
          name="registration"
          className="flex flex-col items-center gap-4 p-20"
          onSubmit={(event) => {
            event.preventDefault();
            signUpMutation.mutate();
          }}
        >
          <h2 className="text-3xl">Registration</h2>
          <div className="flex flex-col">
            <label htmlFor={emailId}>Email</label>
            <input
              id={emailId}
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Email"
              required
            />
          </div>
          <div className="flex w-full flex-col">
            <label htmlFor={passwordId}>Password</label>
            <input
              id={passwordId}
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
            className="mt-[25px] cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
            disabled={signUpMutation.isPending}
          >
            {signUpMutation.isPending ? '...' : 'Sign Up'}
          </button>
        </form>
      </div>
    </div>
  );
}
