-- 修复 chat 表的外键约束问题
-- 问题：外键错误指向 chat 表而不是 session 表

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 删除旧表（包含所有数据）
DROP TABLE IF EXISTS `chat`;

-- 创建正确的 chat 表
CREATE TABLE `chat` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `session_id` int NOT NULL COMMENT '会话id',
  `user_id` int NULL DEFAULT NULL COMMENT '用户id',
  `role` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '角色',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '回复内容',
  `answer_id` int NULL DEFAULT NULL COMMENT '用于排序',
  `deleted` int NULL DEFAULT 0 COMMENT '删除状态',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_session_id`(`session_id` ASC) USING BTREE,
  CONSTRAINT `fk_chat_session` FOREIGN KEY (`session_id`) REFERENCES `session` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_chat_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
