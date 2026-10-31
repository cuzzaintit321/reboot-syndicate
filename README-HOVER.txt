REBOOT SYNDICATE - HOVER-ONLY SERVICE IMAGES

Includes the 14 original service WebP pictures.
The service cards remain black by default and show their respective picture
only on hover or keyboard focus, under a dark text-readable gradient.

On Fedora:
  scp ~/Downloads/reboot_syndicate_hover_images.zip yeet:~/circuit-syndicate/

On yeet:
  cd ~/circuit-syndicate
  python3 -m zipfile -e reboot_syndicate_hover_images.zip .
  python3 apply_hover_images.py
  docker compose up -d --build website

No changes are made to application routes, databases, or customer requests.
You can also pull the latest GitHub CSS update if you prefer; the installer
will notice the existing CSS rules and won't duplicate them.
