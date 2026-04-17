import subprocess

def get_public_xray_key(private_key: str) -> str:
    result = subprocess.check_output(["xray", "x25519", "-i", f"{private_key}"], text=True)
    public_key = result.split("Public key: ")[1].splitlines()[0].strip()
    return public_key


def generate_xray_keys() -> dict[str, str]:
    result = subprocess.check_output(["xray", "x25519"], text=True)
    private_key = result.split("Private key: ")[1].splitlines()[0].strip()
    public_key = result.split("Public key: ")[1].splitlines()[0].strip()

    return {public_key: private_key}
