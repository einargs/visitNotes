{ pkgs, ... }: {
  imports = [
    ./site-service.nix
  ];
  networking.firewall.allowedTCPPorts = [ 80 443 8000 ];
  # we'll use azure to configure our users for us
  users.mutableUsers = true;
  users.users.mtsu.isSystemUser = true;
  users.users.mtsu.initialPassword = "test";
  system.stateVersion = "23.05";
  services.openssh = {
    enable = true;
  };
  services.site-backend = {
    enable = true;
    port = 8000;
  };
}
