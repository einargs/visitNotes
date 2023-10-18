{ pkgs, modulesPath, visit-notes-site, ... }: {
  imports = [
    # For local testing uncomment this
    ./local.nix
    ./site-service.nix
  ];
  networking.firewall.allowedTCPPorts = [ 80 443 8080 ];
  users.mutableUsers = false;
  networking.hostName = "visit-notes";

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
    port = 8080;
  };
  /*security.acme = {
    acceptTerms = true;
    defaults.email = "egs3d@mtmail.mtsu.edu";
  };*/
  services.nginx = {
    enable = true;
    /*httpConfig = ''
      http {
        server {
          listen 80;

          location /socket.io/ {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;

            proxy_pass http://localhost:3000;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
          }
        }
      }
    '';*/
    appendHttpConfig = ''
      upstream site_backend {
        server 127.0.0.1:8080;
      }
    '';
    virtualHosts = {
      "audio.einargs.dev" = {
        # We'll turn this on once we have a certificate
        # forceSSL = true;
        # enableACME = true;
        forceSSL = true;
        # addSSL = true;
        locations."/" = {
          root = "${visit-notes-site}/";
          # priority = 100;
        };
        locations."/socket.io/" = {
          # these duplicate some of the stuff in extraConfig
          # recommendedProxySettings = true;
          # proxyWebsockets = true;
          # priority = 50;
          proxyPass = "http://site_backend"; # The socket.io path is kept
          extraConfig = ''
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
          '';
        };
      };
    };
  };
}
