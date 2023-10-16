{
  description = "Tool for doctors to summarize doctor-patient conversations";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };
  nixConfig = {
    bash-prompt = ''\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '';
  };

  outputs = { self, nixpkgs, poetry2nix }: 
  let system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.permittedInsecurePackages = [
          "openssl-1.1.1v"
        ];
        overlay = [ poetry2nix.overlay ];
      };

      get-azure-inputs = p: with p; [
        stdenv.cc
        gcc
        openssl_1_1
        alsa-lib
        libuuid
        binutils
        util-linux
      ];
      azure-inputs = get-azure-inputs pkgs;

      backend-app-env = (pkgs.poetry2nix.mkPoetryEnv {
        projectDir = ./.;
        python = pkgs.python311;
        preferWheels = true;
        overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
          azure-cognitiveservices-speech = super.azure-cognitiveservices-speech
            .overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [])
                ++ get-azure-inputs pkgs
                ++ [ pkgs.gst_all_1.gstreamer ];
            });
        });
      });
  in {
    devShells.x86_64-linux.default = (pkgs.buildFHSUserEnv {
      name = "audio";
      targetPkgs = pkgs: with pkgs; [
        # vlc
        docker
        python311
        nodejs_20
        nodePackages.pnpm
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

    nixosConfigurations.vm = nixpkgs.lib.nixosSystem {

    };
    packages.x86_64-linux.default = backend-app-env;

    /* I am giving up on docker for right now and instead switching to a nixos
     * vm.
    packages.x86_64-linux.default = with pkgs; pkgs.dockerTools.buildImage {
      name = "visit-notes";
      tag = "latest";
      copyToRoot = buildEnv {
        name = "image-root";
        pathsToLink = [ "/bin" ];
        paths = [
          dockerTools.fakeNss
          backend-app-env
        ];
      };
      config = {
        Cmd = [ "hypercorn" "app:asgi" "-b" "0.0.0.0:80" "--root-path" "${./.}" ];
        ExposedPorts = {
          "80/tcp" = {};
        };
      };
    };*/
  };
}
