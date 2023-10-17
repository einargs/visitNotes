{ pkgs, modulesPath, ... }: {
  imports = [
    # FOR LOCAL YOU ALSO NEED TO UNCOMMENT THIS
    # "${modulesPath}/virtualisation/qemu-vm.nix"
    ./site-service.nix
  ];
  networking.firewall.allowedTCPPorts = [ 80 443 8000 ];
  # we'll use azure to configure our users for us
  # users.mutableUsers = true;
  users.mutableUsers = false;
  networking.hostName = "visit-notes";
  /* UNCOMMENT THIS TO MAKE LOCAL TESTING EASY
  networking.firewall.enable = false;
  # When we're locally virtualizing the machine, forward ports so we can test
  # the server
  virtualisation.forwardPorts = [
    { from = "host"; host.port = 8000; guest.port = 80; }
    { from = "host"; host.port = 8022; guest.port = 22; }
  ];*/
  users.users.mtsu = {
    isNormalUser = true;
    home = "/home/mtsu";
    description = "MTSU student";
    extraGroups =
      [ "wheel" # users in wheel are allowed to use sudo
        "disk" "audio" "video" "networkmanager" "systemd-journal"
      ];
    hashedPassword = "$y$j9T$vsRtWjpE4252XW/6CASe3/$wptn/nGTeXFNI1jYEkx1ejVlz6DzoYSNMWDFfhLUF18";
  };
  system.stateVersion = "23.05";
  services.openssh = {
    enable = true;
  };
  services.site-backend = {
    enable = true;
    port = 80;
  };
}
