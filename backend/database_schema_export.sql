========================================================================================================================
SMARTMETER DATABASE - ALL TABLES SCHEMA (MySQL)
========================================================================================================================


########################################################################################################################
# TABLE 1: AUTH_GROUP
########################################################################################################################

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 2: AUTH_GROUP_PERMISSIONS
########################################################################################################################

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 3: AUTH_PERMISSION
########################################################################################################################

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 52
-- Status: ✓ 52 rows


########################################################################################################################
# TABLE 4: DJANGO_ADMIN_LOG
########################################################################################################################

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 5: DJANGO_CONTENT_TYPE
########################################################################################################################

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 13
-- Status: ✓ 13 rows


########################################################################################################################
# TABLE 6: DJANGO_MIGRATIONS
########################################################################################################################

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 29
-- Status: ✓ 29 rows


########################################################################################################################
# TABLE 7: DJANGO_SESSION
########################################################################################################################

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 8: ENERGY_ACTIONLOG
########################################################################################################################

CREATE TABLE `energy_actionlog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `action` varchar(100) NOT NULL,
  `details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`details`)),
  `timestamp` datetime(6) NOT NULL,
  `ip_address` char(39) DEFAULT NULL,
  `utilisateur_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `energy_actionlog_timestamp_b3ca37f2` (`timestamp`),
  KEY `energy_acti_utilisa_516fcf_idx` (`utilisateur_id`,`timestamp`),
  KEY `energy_acti_action_bbd4de_idx` (`action`,`timestamp`),
  CONSTRAINT `energy_actionlog_utilisateur_id_e2a1eda7_fk_users_user_id` FOREIGN KEY (`utilisateur_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 6
-- Status: ✓ 6 rows


########################################################################################################################
# TABLE 9: ENERGY_ALERTE
########################################################################################################################

CREATE TABLE `energy_alerte` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `acquittee` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `acquittee_at` datetime(6) DEFAULT NULL,
  `anomalie_id` bigint(20) NOT NULL,
  `statut` varchar(20) NOT NULL,
  `consultee_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `anomalie_id` (`anomalie_id`),
  KEY `energy_aler_acquitt_0931cc_idx` (`acquittee`,`created_at`),
  KEY `energy_alerte_statut_3a3ac9d2` (`statut`),
  KEY `energy_aler_statut_ccac5a_idx` (`statut`,`created_at`),
  KEY `energy_aler_anomali_712bb8_idx` (`anomalie_id`,`statut`),
  KEY `energy_alerte_created_at_0177f792` (`created_at`),
  CONSTRAINT `energy_alerte_anomalie_id_36d23d89_fk_energy_anomalie_id` FOREIGN KEY (`anomalie_id`) REFERENCES `energy_anomalie` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 49
-- Status: ✓ 49 rows


########################################################################################################################
# TABLE 10: ENERGY_ANOMALIE
########################################################################################################################

CREATE TABLE `energy_anomalie` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `score_confiance` double NOT NULL,
  `severite` varchar(20) NOT NULL,
  `statut` varchar(20) NOT NULL,
  `description` longtext DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `consommation_id` bigint(20) NOT NULL,
  `consultee_at` datetime(6) DEFAULT NULL,
  `acquittee_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `consommation_id` (`consommation_id`),
  KEY `energy_anom_statut_78c01c_idx` (`statut`,`created_at`),
  KEY `energy_anomalie_statut_39695eb4` (`statut`),
  KEY `energy_anom_consomm_ba0d48_idx` (`consommation_id`,`statut`),
  CONSTRAINT `energy_anomalie_consommation_id_3144d7ad_fk_energy_co` FOREIGN KEY (`consommation_id`) REFERENCES `energy_consommation` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 49
-- Status: ✓ 49 rows


########################################################################################################################
# TABLE 11: ENERGY_CONSOMMATION
########################################################################################################################

CREATE TABLE `energy_consommation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime(6) NOT NULL,
  `kwh` double NOT NULL,
  `anomaly_label` varchar(50) DEFAULT NULL,
  `temperature` double DEFAULT NULL,
  `foyer_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `energy_consommation_timestamp_e9ad07f1` (`timestamp`),
  KEY `energy_cons_foyer_i_1e3843_idx` (`foyer_id`,`timestamp`),
  KEY `energy_cons_timesta_0d1742_idx` (`timestamp`),
  CONSTRAINT `energy_consommation_foyer_id_d8292a21_fk_energy_foyer_id` FOREIGN KEY (`foyer_id`) REFERENCES `energy_foyer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1009 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 1008
-- Status: ✓ 1008 rows


########################################################################################################################
# TABLE 12: ENERGY_CONSUMPTION_READING
########################################################################################################################

CREATE TABLE `energy_consumption_reading` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `meter_id` varchar(50) NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `consumption_kwh` decimal(10,2) NOT NULL,
  `cost_estimate` decimal(10,2) NOT NULL,
  `tariff_type` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `resident_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_reading_per_resident_meter_timestamp` (`resident_id`,`meter_id`,`timestamp`),
  KEY `energy_consumption_reading_meter_id_cc5e1bef` (`meter_id`),
  KEY `energy_consumption_reading_timestamp_7d26cee4` (`timestamp`),
  KEY `energy_cons_residen_6de389_idx` (`resident_id`,`timestamp`),
  KEY `energy_cons_meter_i_41107f_idx` (`meter_id`,`timestamp`),
  KEY `energy_cons_timesta_4f5cbc_idx` (`timestamp`),
  CONSTRAINT `energy_consumption_reading_resident_id_da1d9af1_fk_users_user_id` FOREIGN KEY (`resident_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 13: ENERGY_CONVERSATIONIA
########################################################################################################################

CREATE TABLE `energy_conversationia` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `question` longtext NOT NULL,
  `reponse` longtext NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `utilisateur_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `energy_conversationIA_timestamp_cc3b9349` (`timestamp`),
  KEY `energy_conv_utilisa_4a7519_idx` (`utilisateur_id`,`timestamp`),
  CONSTRAINT `energy_conversationIA_utilisateur_id_c642419b_fk_users_user_id` FOREIGN KEY (`utilisateur_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 14: ENERGY_FOYER
########################################################################################################################

CREATE TABLE `energy_foyer` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `numero_foyer` varchar(50) NOT NULL,
  `adresse` longtext NOT NULL,
  `code_postal` varchar(10) NOT NULL,
  `ville` varchar(100) NOT NULL,
  `puissance_souscrite` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_foyer` (`numero_foyer`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 6
-- Status: ✓ 6 rows


########################################################################################################################
# TABLE 15: USERS_USER
########################################################################################################################

CREATE TABLE `users_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL,
  `foyer_id` bigint(20) DEFAULT NULL,
  `managed_by_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `users_user_role_36d76d_idx` (`role`),
  KEY `users_user_foyer_i_8b5be2_idx` (`foyer_id`),
  KEY `users_user_managed_by_id_ffb24d7a` (`managed_by_id`),
  KEY `users_user_managed_33327b_idx` (`managed_by_id`),
  CONSTRAINT `users_user_foyer_id_7eb0ab3e_fk_energy_foyer_id` FOREIGN KEY (`foyer_id`) REFERENCES `energy_foyer` (`id`),
  CONSTRAINT `users_user_managed_by_id_ffb24d7a_fk_users_user_id` FOREIGN KEY (`managed_by_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 7
-- Status: ✓ 7 rows


########################################################################################################################
# TABLE 16: USERS_USER_GROUPS
########################################################################################################################

CREATE TABLE `users_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_groups_user_id_group_id_b88eab82_uniq` (`user_id`,`group_id`),
  KEY `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY


########################################################################################################################
# TABLE 17: USERS_USER_USER_PERMISSIONS
########################################################################################################################

CREATE TABLE `users_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_user_permissions_user_id_permission_id_43338c45_uniq` (`user_id`,`permission_id`),
  KEY `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci


-- Total Rows: 0
-- Status: ✓ EMPTY
