{ config, pkgs, lib, visit-notes-site, visit-notes-app, transcript-file, ... }:

let cfg = config.services.site-backend; in
with lib;

{
  options = {
    services.site-backend = {
      enable = mkEnableOption "site-backend";

      port = mkOption {
        type = with types; nullOr port;
        default = 80;
        example = 8000;
        description = "The port to bind the server to.";
      };
    };
  };

  config = mkIf cfg.enable {
    systemd.services.site-backend = {
      # TODO: figure out how to setup the proper user.
      description = "recipe-ocr server";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      path = with pkgs; [ tesseract4 ];
      environment = {
        ENV_FILE = "/var/lib/site-backend/env-file";
        PORT = builtins.toString cfg.port;
        TRANSCRIPT = "${transcript-file}";
        STATIC_FILES = "${visit-notes-site}";
      };
      serviceConfig = {
        StateDirectory = "site-backend";
        ExecStart = "${visit-notes-app}/bin/visit-notes";
      };
    };
  };
}
