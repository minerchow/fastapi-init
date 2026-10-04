/*
 Navicat Premium Dump SQL

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 80012 (8.0.12)
 Source Host           : localhost:3306
 Source Schema         : app_db

 Target Server Type    : MySQL
 Target Server Version : 80012 (8.0.12)
 File Encoding         : 65001

 Date: 15/09/2026 17:37:24
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('782f2e8edc1b');

-- ----------------------------
-- Table structure for article
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(11) NULL DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_article_user_id`(`user_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of article
-- ----------------------------
INSERT INTO `article` VALUES (1, 'aaa5', 'dd4', '2026-05-04 15:54:50', '2026-07-12 10:20:26', 1, 0);
INSERT INTO `article` VALUES (2, 'aaa4', 'xx2', '2026-05-04 15:55:27', '2026-05-04 17:29:23', 1, 0);
INSERT INTO `article` VALUES (3, 'aa11', 'xx2222', '2026-05-04 17:41:07', '2026-05-04 17:41:07', 1, 0);
INSERT INTO `article` VALUES (4, '文111', '文章内容22', '2026-09-08 02:12:36', '2026-09-08 02:17:13', 2, 0);

-- ----------------------------
-- Table structure for permission
-- ----------------------------
DROP TABLE IF EXISTS `permission`;
CREATE TABLE `permission`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `is_deleted` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `code`(`code`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permission
-- ----------------------------
INSERT INTO `permission` VALUES (1, 'article:read', '查看文章', '查看文章列表和详情', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (2, 'article:create', '创建文章', '创建新文章', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (3, 'article:update', '更新文章', '修改文章内容', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (4, 'article:update:own', '更新自己的文章', '仅修改自己创建的文章', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (5, 'article:delete', '删除文章', '删除任意文章', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (6, 'article:delete:own', '删除自己的文章', '仅删除自己创建的文章', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (7, 'user:read', '查看用户', '查看用户列表', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (8, 'user:create', '创建用户', '注册新用户', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (9, 'user:update', '修改用户', '修改用户信息', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (10, 'user:delete', '删除用户', '删除用户', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (11, 'user:assign_role', '分配角色', '给用户分配角色', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (12, 'role:read', '查看角色', '查看角色列表', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (13, 'role:create', '创建角色', '创建新角色', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (14, 'role:update', '修改角色', '修改角色信息和权限', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `permission` VALUES (15, 'role:delete', '删除角色', '删除角色', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `is_deleted` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of role
-- ----------------------------
INSERT INTO `role` VALUES (1, 'admin', '管理员，拥有所有权限', 0, '2026-09-08 01:57:26', '2026-09-08 01:57:26');
INSERT INTO `role` VALUES (2, 'author', '作者，可以创建和管理自己的文章', 0, '2026-09-08 01:57:56', '2026-09-08 01:57:56');
INSERT INTO `role` VALUES (3, 'user', '普通用户，仅能查看文章', 0, '2026-09-08 01:57:56', '2026-09-08 01:57:56');

-- ----------------------------
-- Table structure for role_permission
-- ----------------------------
DROP TABLE IF EXISTS `role_permission`;
CREATE TABLE `role_permission`  (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `permission_id`(`permission_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Fixed;

-- ----------------------------
-- Records of role_permission
-- ----------------------------
INSERT INTO `role_permission` VALUES (1, 1);
INSERT INTO `role_permission` VALUES (1, 2);
INSERT INTO `role_permission` VALUES (1, 3);
INSERT INTO `role_permission` VALUES (1, 4);
INSERT INTO `role_permission` VALUES (1, 5);
INSERT INTO `role_permission` VALUES (1, 6);
INSERT INTO `role_permission` VALUES (1, 7);
INSERT INTO `role_permission` VALUES (1, 8);
INSERT INTO `role_permission` VALUES (1, 9);
INSERT INTO `role_permission` VALUES (1, 10);
INSERT INTO `role_permission` VALUES (1, 11);
INSERT INTO `role_permission` VALUES (1, 12);
INSERT INTO `role_permission` VALUES (1, 13);
INSERT INTO `role_permission` VALUES (1, 14);
INSERT INTO `role_permission` VALUES (1, 15);
INSERT INTO `role_permission` VALUES (2, 1);
INSERT INTO `role_permission` VALUES (2, 2);
INSERT INTO `role_permission` VALUES (2, 4);
INSERT INTO `role_permission` VALUES (2, 6);
INSERT INTO `role_permission` VALUES (3, 1);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username_UNIQUE`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'xiaoming', '$2b$12$DnZ2ciQ5rJa4SuX6iNYopukir1mSS8s/7aVN0S0thzGQim2LlWvSm', NULL, NULL, '2026-05-04 11:56:14', '2026-05-04 16:59:43', 0);
INSERT INTO `user` VALUES (2, 'xiaoming2', '$2b$12$knGhyOYS5W6c34Y70El7IurvKQIkH03SuKA0vvgBNeimdlmprQUC6', NULL, NULL, '2026-05-04 14:45:57', '2026-05-04 17:42:50', 0);
INSERT INTO `user` VALUES (3, 'test', '$2b$12$Qfx5pKrGaoSxhpXON1639OTU1ZepSQMfYiqHcHgeaUks.8wKfYk1G', NULL, NULL, '2026-09-10 02:01:17', '2026-09-10 02:01:17', 0);
INSERT INTO `user` VALUES (4, 'xiaoming8', '$2b$12$LuSWsakjUWsoeP.zaQmlvuH7t6tYBJwBR3dHc7VnRy6mAoZvqJ1kG', NULL, NULL, '2026-09-11 01:42:12', '2026-09-11 01:42:12', 0);

-- ----------------------------
-- Table structure for user_role
-- ----------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role`  (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Fixed;

-- ----------------------------
-- Records of user_role
-- ----------------------------
INSERT INTO `user_role` VALUES (1, 1);
INSERT INTO `user_role` VALUES (2, 3);

SET FOREIGN_KEY_CHECKS = 1;
