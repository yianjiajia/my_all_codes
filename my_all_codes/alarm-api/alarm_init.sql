CREATE TABLE `sys_items` (

  `sys_item_id` INTEGER AUTO_INCREMENT NOT NULL,

  `user_id`     VARCHAR(64)            NOT NULL,

  `item_id`     BIGINT UNSIGNED        NOT NULL,

  `created_at`  TIMESTAMP              NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (sys_item_id)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_graphs` (

  `sys_graph_id`  INTEGER AUTO_INCREMENT NOT NULL,

  `user_id`       VARCHAR(64)            NOT NULL,

  `graph_id`      BIGINT UNSIGNED        NOT NULL,

  `resource_name` VARCHAR(64)            NOT NULL,

  `region`        VARCHAR(32)            NOT NULL,

  `graph_type`    VARCHAR(20)            NOT NULL,

  `created_at`    TIMESTAMP              NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (sys_graph_id)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_notices` (

  `notice_id`     INTEGER AUTO_INCREMENT NOT NULL,

  `user_id`       VARCHAR(64)            NOT NULL,

  `mobile_number` VARCHAR(16),

  `email`         VARCHAR(64),

  `comment`       MEDIUMTEXT,

  `created_at`    TIMESTAMP              NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (notice_id)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_triggers` (

  `strigger_id`  INTEGER AUTO_INCREMENT  NOT NULL,

  `user_id`      VARCHAR(64)             NOT NULL,

  `trigger_name` VARCHAR(255) DEFAULT '' NOT NULL,

  `trigger_type` VARCHAR(64)             NOT NULL,

  `mobile`       VARCHAR(10),

  `email`        VARCHAR(10),

  `created_at`   TIMESTAMP               NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (strigger_id)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_triggers_objects` (

  `trigger_object_id` INTEGER AUTO_INCREMENT NOT NULL,

  `strigger_id`       INTEGER                NOT NULL,

  `object_id`         VARCHAR(64)            NOT NULL,

  `object_type`       VARCHAR(16)            NOT NULL,

  `object_name`       VARCHAR(128) DEFAULT '' NOT NULL,

  `trigger_id`        BIGINT UNSIGNED,

  PRIMARY KEY (trigger_object_id),

  CONSTRAINT `c_triggers_objects` FOREIGN KEY (`strigger_id`) REFERENCES `sys_triggers` (`strigger_id`)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_alarm_logs` (

  `sys_trigger_log_id` INTEGER AUTO_INCREMENT NOT NULL,

  `user_id`            VARCHAR(64)            NOT NULL,

  `alarm_object_name`  VARCHAR(64)            NOT NULL,

  `alarm_content`      MEDIUMTEXT             NOT NULL,

  `alarm_status`       VARCHAR(16)            NOT NULL,

  `trigger_name`       VARCHAR(64)            NOT NULL,

  `trigger_type`       VARCHAR(16)            NOT NULL,

  `occurred_at`        DATETIME,

  `ended_at`           DATETIME,

  `event_id`           BIGINT UNSIGNED        NOT NULL,

  PRIMARY KEY (sys_trigger_log_id)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;


CREATE TABLE `sys_triggers_items` (

  `sys_trigger_item_id` INTEGER AUTO_INCREMENT NOT NULL,

  `strigger_id`         INTEGER                NOT NULL,

  `item_name`           VARCHAR(64)            NOT NULL,

  `operator`            VARCHAR(16)            NOT NULL,

  `value`               VARCHAR(64)            NOT NULL,

  `keep_time`           VARCHAR(10)            NOT NULL,

  PRIMARY KEY (sys_trigger_item_id),

  CONSTRAINT `c_sys_trigger_items` FOREIGN KEY (`strigger_id`) REFERENCES `sys_triggers` (`strigger_id`)

)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8
  COLLATE = utf8_bin;