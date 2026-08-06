-- 为菜谱封面增加缩略图对象键，旧菜谱为空时继续使用原图。
ALTER TABLE `recipes`
    ADD COLUMN `cover_processed_object_key` VARCHAR(512) NULL COMMENT '菜谱封面缩略图在对象存储中的文件键，未生成时为空'
        AFTER `cover_object_key`;
