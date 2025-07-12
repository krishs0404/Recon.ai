import Image from 'next/image';

export default function Header() {
  return (
    <header className="bg-black h-20 flex items-center justify-center">
      <Image src="/recon_logo.png" alt="Recon Logo" width={40} height={40} />
    </header>
  );
} 