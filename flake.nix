{
  description = "Tool for doctors to summarize doctor-patient conversations";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
    nixos-generators = {
      url = "github:nix-community/nixos-generators";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  nixConfig = {
    bash-prompt = ''\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '';
  };

  outputs = { self, nixpkgs, poetry2nix, nixos-generators }: 
  let system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.permittedInsecurePackages = [
          "openssl-1.1.1v"
        ];
        overlay = [ poetry2nix.overlay ];
      };

      azure-inputs = with pkgs; [
        stdenv.cc
        gcc
        openssl_1_1
        alsa-lib
        libuuid
        binutils
        util-linux
      ];

      # Still don't know if this properly has everything and I can actually run
      # stuff but we'll find out. I might need to use root path, I might be able
      # to use python module syntax to get at an installed version of it?
      # Probably just use root-path.
      backend-app-env = (pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ./.;
        src = ./src;
        python = pkgs.python311;
        preferWheels = true;
        overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          azure-cognitiveservices-speech = super.azure-cognitiveservices-speech
            .overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [])
                ++ azure-inputs
                ++ [ pkgs.gst_all_1.gstreamer ];
            });
        });
      });
      # The actually built site.
      site-dist = pkgs.callPackage ./notes-site/site-dist.nix {};
      transcript-file = ../data/clean_transcripts/CAR0001.txt;

      # Here we include all the dependencies that it needs
      visit-notes-for = script: pkgs.symlinkJoin {
        name = "visit-notes";

        paths = [
          (pkgs.writeShellScriptBin "visit-notes" script)
          backend-app-env
          pkgs.openssl_1_1.out
          pkgs.gst_all_1.gstreamer
        ] ++ azure-inputs;
        buildInputs = [ pkgs.makeWrapper ];
        postBuild = ''
          wrapProgram $out/bin/visit-notes --prefix PATH : $out/bin \
            --prefix LD_LIBRARY_PATH : $out/lib
        '';
      };
      # TODO: use poetry2nix script or filter ./. with the tool poetry uses
      # so whole package isn't put in the store
      visit-notes-vm-app = visit-notes-for ''
        hypercorn ${./src}/app:asgi -b 127.0.0.1:$PORT
      '';
      visit-notes-docker-app = visit-notes-for ''
        hypercorn ${./src}/app:asgi -b 0.0.0.0:80
      '';
      visit-notes-docker = with pkgs; pkgs.dockerTools.buildImage {
        name = "visit-notes";
        tag = "latest";
        copyToRoot = buildEnv {
          name = "image-root";
          pathsToLink = [ "/bin" "/lib" "/etc" ];
          paths = let 
            # Enable this if we want it to be able to enter a shell
            needs-shell = false;
            shell-inputs = if needs-shell then [
              dockerTools.usrBinEnv
              dockerTools.binSh
              vim
              coreutils
              dockerTools.fakeNss
              backend-app-env
            ] else [];

          in [
            dockerTools.caCertificates
            visit-notes-docker-app
          ] ++ shell-inputs;
        };
        config = {
          Env = [
            # This makes sure that if we run hypercorn inside the shell it can
            # see the openssl libraries. Not needed right now. You'd also need
            # to include the openssl libraries in the buildEnv
            # "LD_LIBRARY_PATH=/lib"
            "MODULES=${./src}"
            "TRANSCRIPT=${./data/clean_transcripts/CAR0001.txt}"
            "STATIC_FILES=${site-dist}"
          ];
          Cmd = [ "${visit-notes-app}/bin/visit-notes" ];
          # If we wanted to call it directly, which would be a pain.
          # Cmd = [ "hypercorn" "${./.}/app:asgi" "-b" "0.0.0.0:80" ];
          ExposedPorts = {
            "80/tcp" = {};
          };
        };
      };
      azure-image = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        specialArgs = {
          visit-notes-site = site-dist;
          visit-notes-app = visit-notes-vm-app;
          inherit transcript-file;
        };
        modules = [
          nixos-generators.nixosModules.all-formats
          ./vm/config.nix
        ];
      };
  in {
    devShells.x86_64-linux.default = (pkgs.buildFHSUserEnv {
      name = "audio";
      targetPkgs = pkgs: with pkgs; [
        # vlc
        azure-cli
        docker
        python311
        nodejs_20
        nodePackages.pnpm
        prefetch-npm-deps
        poetry

        wget
        curl
        autoconf
        git
        gitRepo
        gnumake
        unzip
      ] ++ azure-inputs;

        # export PS1='\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '
      profile = ''
        source .venv/bin/activate
      ''; # may add commandline call to dotenv to load from .env
        # virtualenv .venv

      /*src = [
       ./flake.nix
       ./flake.lock
      ];*/

      /*shellHook = ''
        virtualenv .venv
        source .venv/bin/activate
      '';*/

      /*unpackPhase = ''
        for srcFile in $src; do
          cp $srcFile $(stripHash $srcFile)
        done
      '';*/ 
    }).env;

    # To get an image we can deploy to azure do:
    # nix build .#nixosConfigurations.my-machine.config.formats.azure
    nixosConfigurations.azure-vm = azure-image;

    nixosModules.backend = args: import ./vm/site-service.nix ({
      visit-notes-site = site-dist;
      visit-notes-app = visit-notes-vm-app;
      inherit transcript-file;
    } // args);

    packages.x86_64-linux = {
      vm-app = visit-notes-vm-app;
      site = site-dist;
      docker = visit-notes-docker;
    };
  };
}
