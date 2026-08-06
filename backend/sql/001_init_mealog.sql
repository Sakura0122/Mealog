-- Mealog 数据库：保存用户、饮食记录、店铺、个人菜谱及菜谱分享状态，适用于 MySQL 8.0.16 及以上版本。
-- 设计说明：数据库仅约束用户身份唯一性；其余关联完整性、枚举值、业务唯一性、级联删除及图片规则由应用层事务维护。
-- 软删除说明：业务删除时写入 deleted_at，默认查询仅返回 deleted_at IS NULL 的数据；恢复及最终物理清理由应用层处理。
CREATE DATABASE IF NOT EXISTS `mealog`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `mealog`;

-- 用户表：保存微信用户身份和个人资料，是所有私人业务数据的归属主体。
CREATE TABLE IF NOT EXISTS `users`
(
    `id`             CHAR(36)      NOT NULL COMMENT '用户主键 UUID',
    `wechat_openid`  VARCHAR(64)   NOT NULL COMMENT '微信小程序用户 OpenID',
    `wechat_unionid` VARCHAR(64)   NULL COMMENT '微信开放平台 UnionID，未绑定开放平台时为空',
    `nickname`       VARCHAR(64)   NULL COMMENT '用户昵称',
    `avatar_object_key` VARCHAR(512) NULL COMMENT '用户头像在对象存储中的文件键',
    `created_at`     DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at`     DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at`     DATETIME(3)   NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_users_wechat_openid` (`wechat_openid`),
    KEY `idx_users_wechat_unionid_deleted` (`wechat_unionid`, `deleted_at`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '用户表，保存微信身份和个人资料';

-- 店铺表：保存用户从腾讯地图选择的店铺，供历史记录复用。
CREATE TABLE IF NOT EXISTS `stores`
(
    `id`              CHAR(36)       NOT NULL COMMENT '店铺主键 UUID',
    `user_id`         CHAR(36)       NOT NULL COMMENT '店铺所属用户 UUID',
    `name`            VARCHAR(128)   NOT NULL COMMENT '店铺名称',
    `address`         VARCHAR(255)   NULL COMMENT '店铺地址',
    `latitude`        DECIMAL(10, 7) NULL COMMENT '店铺纬度，范围 -90 到 90',
    `longitude`       DECIMAL(10, 7) NULL COMMENT '店铺经度，范围 -180 到 180',
    `created_at`      DATETIME(3)    NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at`      DATETIME(3)    NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at`      DATETIME(3)    NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    KEY `idx_stores_user_deleted_name` (`user_id`, `deleted_at`, `name`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '店铺表，保存外食记录可关联的腾讯地图店铺';

-- 菜谱表：保存用户的菜谱草稿和已完善菜谱，并记录从分享菜谱复制时的来源关系。
CREATE TABLE IF NOT EXISTS `recipes`
(
    `id`               CHAR(36)     NOT NULL COMMENT '菜谱主键 UUID',
    `user_id`          CHAR(36)     NOT NULL COMMENT '菜谱所属用户 UUID',
    `source_recipe_id` CHAR(36)     NULL COMMENT '从分享页保存时对应的原菜谱 UUID，自建菜谱为空',
    `name`             VARCHAR(100) NOT NULL COMMENT '菜谱名称，同一用户下不可重复',
    `cover_object_key` VARCHAR(512) NULL COMMENT '菜谱封面在对象存储中的文件键',
    `steps`            TEXT         NULL COMMENT '菜谱制作步骤',
    `status`           VARCHAR(20)  NOT NULL DEFAULT 'DRAFT' COMMENT '菜谱状态：DRAFT 草稿，COMPLETED 已完善，由应用层根据食材和步骤计算并校验',
    `share_expires_at` DATETIME(3)  NULL COMMENT '分享过期时间，为空或早于当前时间表示不可访问',
    `created_at`       DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at`       DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at`       DATETIME(3)  NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    KEY `idx_recipes_user_deleted_name` (`user_id`, `deleted_at`, `name`),
    KEY `idx_recipes_user_deleted_status_updated` (`user_id`, `deleted_at`, `status`, `updated_at`),
    KEY `idx_recipes_source_recipe_deleted` (`source_recipe_id`, `deleted_at`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '菜谱表，保存个人菜谱草稿、完整菜谱及分享复制来源';

-- 菜谱食材表：按录入顺序保存菜谱中的食材标签，一条记录表示一种食材。
CREATE TABLE IF NOT EXISTS `recipe_ingredients`
(
    `id`         CHAR(36)          NOT NULL COMMENT '菜谱食材主键 UUID',
    `recipe_id`  CHAR(36)          NOT NULL COMMENT '所属菜谱 UUID',
    `name`       VARCHAR(100)      NOT NULL COMMENT '食材名称',
    `sort_order` SMALLINT UNSIGNED NOT NULL COMMENT '食材展示顺序，从 0 开始',
    `created_at` DATETIME(3)       NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at` DATETIME(3)       NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at` DATETIME(3)       NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    KEY `idx_recipe_ingredients_recipe_deleted_name` (`recipe_id`, `deleted_at`, `name`),
    KEY `idx_recipe_ingredients_recipe_deleted_order` (`recipe_id`, `deleted_at`, `sort_order`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '菜谱食材表，保存菜谱的有序食材列表';

-- 饮食记录表：保存用户某次吃到的一道菜，包括时间、来源、关联店铺或菜谱以及个人备注。
CREATE TABLE IF NOT EXISTS `meal_records`
(
    `id`          CHAR(36)      NOT NULL COMMENT '饮食记录主键 UUID',
    `user_id`     CHAR(36)      NOT NULL COMMENT '饮食记录所属用户 UUID',
    `dish_name`   VARCHAR(100)  NOT NULL COMMENT '菜品名称，一条记录只描述一道菜品',
    `eaten_at`    DATETIME(3)   NOT NULL COMMENT '进食时间',
    `source_type` VARCHAR(20)   NULL COMMENT '饮食来源：SELF_MADE 自己做，DINING_OUT 外面买，未选择时为空，由应用层校验',
    `store_id`    CHAR(36)      NULL COMMENT '外面买时可关联的店铺 UUID',
    `recipe_id`   CHAR(36)      NULL COMMENT '自己做时可关联的菜谱 UUID',
    `note`        VARCHAR(1000) NULL COMMENT '本次饮食记录的个人备注',
    `created_at`  DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at`  DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at`  DATETIME(3)   NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    KEY `idx_meal_records_user_deleted_eaten_at` (`user_id`, `deleted_at`, `eaten_at`),
    KEY `idx_meal_records_user_deleted_created_at` (`user_id`, `deleted_at`, `created_at`),
    KEY `idx_meal_records_store_deleted` (`store_id`, `deleted_at`),
    KEY `idx_meal_records_recipe_deleted` (`recipe_id`, `deleted_at`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '饮食记录表，保存单道菜品的时间、来源、关联和备注';

-- 饮食记录图片表：保存一条饮食记录的原图、缩略图、封面标记和展示顺序。
CREATE TABLE IF NOT EXISTS `meal_record_images`
(
    `id`                   CHAR(36)         NOT NULL COMMENT '饮食记录图片主键 UUID',
    `meal_record_id`       CHAR(36)         NOT NULL COMMENT '所属饮食记录 UUID',
    `original_object_key`  VARCHAR(512)     NOT NULL COMMENT '原始图片在对象存储中的文件键',
    `processed_object_key` VARCHAR(512)     NULL COMMENT '缩略图在对象存储中的文件键，未生成时为空',
    `sort_order`           TINYINT UNSIGNED NOT NULL COMMENT '图片展示顺序，从 0 开始，单条记录最多 9 张，由应用层校验',
    `is_cover`             TINYINT(1)       NOT NULL DEFAULT 0 COMMENT '是否为当前记录封面：0 否，1 是，由应用层保证单封面',
    `created_at`           DATETIME(3)      NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    `updated_at`           DATETIME(3)      NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    `deleted_at`           DATETIME(3)      NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    KEY `idx_meal_record_images_record_deleted_order` (`meal_record_id`, `deleted_at`, `sort_order`),
    KEY `idx_meal_record_images_record_deleted_cover` (`meal_record_id`, `deleted_at`, `is_cover`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
    COMMENT = '饮食记录图片表，保存原图、缩略图、顺序和封面标记';
