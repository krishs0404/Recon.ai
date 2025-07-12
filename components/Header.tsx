import Image from 'next/image';

export default function Header() {
  return (
    <header className="bg-black h-24 flex items-center justify-center">
      <Image src="/recon_logo.png" alt="Recon Logo" width={64} height={64} />
    </header>
  );
} 