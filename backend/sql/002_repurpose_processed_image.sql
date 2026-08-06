-- 将 processed_object_key 从预留的抠图结果字段改为饮食记录缩略图字段。
ALTER TABLE `meal_record_images`
    MODIFY COLUMN `processed_object_key` VARCHAR(512) NULL COMMENT '缩略图在对象存储中的文件键，未生成时为空',
    COMMENT = '饮食记录图片表，保存原图、缩略图、顺序和封面标记';
