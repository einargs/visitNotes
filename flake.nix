{
  description = "Tool for doctors to summarize doctor-patient conversations";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";
  };
  nixConfig = {
    bash-prompt = ''\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '';
  };

  outputs = { self, nixpkgs }: 
  let system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.permittedInsecurePackages = [
          "openssl-1.1.1v"
        ];
      };
      # We have to do this
      # pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.x86_64-linux.default = (pkgs.buildFHSUserEnv {
      name = "audio";
      targetPkgs = pkgs: with pkgs; [
        vlc
        # alsa-lib
        chromium
        python311Packages.virtualenv
        python311
        nodejs_20
        nodePackages.pnpm
        gcc
        openssl_1_1
        # libuuid
        autoconf
        binutils
        curl
        git
        gitRepo
        gnumake
        stdenv.cc
        unzip
        util-linux
        wget
      ];
      /*src = [
       ./flake.nix
       ./flake.lock
      ];*/

      # shellHook = ''
      /*shellHook = ''
        virtualenv .venv
        source .venv/bin/activate
      '';*/
      # ./secret_keys is a file exporting SPEECH_KEY and SPEECH_REGION
      profile = ''
        PS1='\[\033[1;32m\][\[\e]0;\u@\h: \w\a\]dev-shell:\w]\$\[\033[0m\] '
        virtualenv .venv
        source .venv/bin/activate
        source ./secret_keys
      '';

      /*unpackPhase = ''
        for srcFile in $src; do
          cp $srcFile $(stripHash $srcFile)
        done
      '';*/ 
    }).env;

  };
}
