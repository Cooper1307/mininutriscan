# app/models/education.py
# 教育内容数据模型

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base

class ContentType(enum.Enum):
    """
    内容类型枚举
    """
    ARTICLE = "article"        # 文章
    VIDEO = "video"            # 视频
    INFOGRAPHIC = "infographic" # 信息图
    QUIZ = "quiz"              # 测验
    RECIPE = "recipe"          # 食谱
    TIP = "tip"                # 小贴士
    FAQ = "faq"                # 常见问题

class ContentStatus(enum.Enum):
    """
    内容状态枚举
    """
    DRAFT = "draft"            # 草稿
    REVIEW = "review"          # 待审核
    PUBLISHED = "published"    # 已发布
    ARCHIVED = "archived"      # 已归档
    DELETED = "deleted"        # 已删除

class DifficultyLevel(enum.Enum):
    """
    难度等级枚举
    """
    BEGINNER = "beginner"      # 初级
    INTERMEDIATE = "intermediate" # 中级
    ADVANCED = "advanced"      # 高级

class TargetAudience(enum.Enum):
    """
    目标受众枚举
    """
    GENERAL = "general"        # 普通用户
    ELDERLY = "elderly"        # 老年人
    CHILDREN = "children"      # 儿童
    PREGNANT = "pregnant"      # 孕妇
    DIABETIC = "diabetic"      # 糖尿病患者
    HYPERTENSION = "hypertension" # 高血压患者
    WEIGHT_LOSS = "weight_loss"   # 减肥人群

class EducationContent(Base):
    """
    教育内容数据模型
    存储营养健康科普教育内容
    """
    __tablename__ = "education_contents"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="内容ID")
    
    # 内容基本信息
    title = Column(String(200), nullable=False, comment="标题")
    subtitle = Column(String(300), nullable=True, comment="副标题")
    content_type = Column(Enum(ContentType), nullable=False, comment="内容类型")
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT, comment="内容状态")
    
    # 内容详情
    summary = Column(Text, nullable=True, comment="内容摘要")
    content = Column(Text, nullable=False, comment="正文内容")
    content_html = Column(Text, nullable=True, comment="HTML格式内容")
    
    # 媒体资源
    cover_image = Column(String(500), nullable=True, comment="封面图片URL")
    images = Column(JSON, nullable=True, comment="图片列表")
    videos = Column(JSON, nullable=True, comment="视频列表")
    attachments = Column(JSON, nullable=True, comment="附件列表")
    
    # 分类和标签
    category = Column(String(50), nullable=False, comment="分类")
    subcategory = Column(String(50), nullable=True, comment="子分类")
    tags = Column(JSON, nullable=True, comment="标签列表")
    keywords = Column(JSON, nullable=True, comment="关键词")
    
    # 目标受众
    target_audience = Column(Enum(TargetAudience), default=TargetAudience.GENERAL, comment="目标受众")
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER, comment="难度等级")
    age_range = Column(String(20), nullable=True, comment="适用年龄范围")
    
    # 内容属性
    reading_time = Column(Integer, nullable=True, comment="预计阅读时间(分钟)")
    word_count = Column(Integer, nullable=True, comment="字数")
    language = Column(String(10), default="zh-CN", comment="语言")
    
    # 营养知识点
    nutrition_topics = Column(JSON, nullable=True, comment="涉及的营养话题")
    health_conditions = Column(JSON, nullable=True, comment="相关健康状况")
    food_categories = Column(JSON, nullable=True, comment="相关食物类别")
    
    # 互动元素
    has_quiz = Column(Boolean, default=False, comment="是否包含测验")
    quiz_questions = Column(JSON, nullable=True, comment="测验题目")
    interactive_elements = Column(JSON, nullable=True, comment="交互元素")
    
    # 作者信息
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="作者ID")
    author_name = Column(String(100), nullable=True, comment="作者姓名")
    author_title = Column(String(100), nullable=True, comment="作者职称")
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审核人ID")
    
    # 发布信息
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    scheduled_at = Column(DateTime, nullable=True, comment="计划发布时间")
    expires_at = Column(DateTime, nullable=True, comment="过期时间")
    
    # 统计数据
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数")
    share_count = Column(Integer, default=0, comment="分享次数")
    comment_count = Column(Integer, default=0, comment="评论数")
    bookmark_count = Column(Integer, default=0, comment="收藏数")
    
    # 评分和反馈
    average_rating = Column(Float, nullable=True, comment="平均评分")
    rating_count = Column(Integer, default=0, comment="评分次数")
    helpful_count = Column(Integer, default=0, comment="有用评价数")
    
    # SEO优化
    meta_description = Column(String(300), nullable=True, comment="SEO描述")
    meta_keywords = Column(String(200), nullable=True, comment="SEO关键词")
    slug = Column(String(200), nullable=True, unique=True, comment="URL别名")
    
    # 推荐算法
    priority_score = Column(Float, default=0.0, comment="优先级评分")
    trending_score = Column(Float, default=0.0, comment="热度评分")
    quality_score = Column(Float, default=0.0, comment="质量评分")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    last_viewed_at = Column(DateTime, nullable=True, comment="最后查看时间")
    
    # 其他设置
    is_featured = Column(Boolean, default=False, comment="是否为推荐内容")
    is_premium = Column(Boolean, default=False, comment="是否为付费内容")
    allow_comments = Column(Boolean, default=True, comment="是否允许评论")
    is_searchable = Column(Boolean, default=True, comment="是否可搜索")
    
    def __repr__(self):
        return f"<EducationContent(id={self.id}, title={self.title}, type={self.content_type}, status={self.status})>"
    
    def to_dict(self, include_content=True):
        """
        转换为字典格式
        
        Args:
            include_content: 是否包含正文内容
            
        Returns:
            教育内容字典
        """
        data = {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "content_type": self.content_type.value if self.content_type else None,
            "status": self.status.value if self.status else None,
            "summary": self.summary,
            "cover_image": self.cover_image,
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags,
            "target_audience": self.target_audience.value if self.target_audience else None,
            "difficulty_level": self.difficulty_level.value if self.difficulty_level else None,
            "reading_time": self.reading_time,
            "word_count": self.word_count,
            "language": self.language,
            "author_name": self.author_name,
            "author_title": self.author_title,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "bookmark_count": self.bookmark_count,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "helpful_count": self.helpful_count,
            "is_featured": self.is_featured,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_content:
            data.update({
                "content": self.content,
                "content_html": self.content_html,
                "images": self.images,
                "videos": self.videos,
                "attachments": self.attachments,
                "keywords": self.keywords,
                "age_range": self.age_range,
                "nutrition_topics": self.nutrition_topics,
                "health_conditions": self.health_conditions,
                "food_categories": self.food_categories,
                "has_quiz": self.has_quiz,
                "quiz_questions": self.quiz_questions,
                "interactive_elements": self.interactive_elements,
                "meta_description": self.meta_description,
                "meta_keywords": self.meta_keywords,
                "slug": self.slug,
                "priority_score": self.priority_score,
                "trending_score": self.trending_score,
                "quality_score": self.quality_score,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                "allow_comments": self.allow_comments,
                "is_searchable": self.is_searchable
            })
        
        return data
    
    def update_status(self, status: ContentStatus, reviewer_id=None):
        """
        更新内容状态
        
        Args:
            status: 新状态
            reviewer_id: 审核人ID（如果是审核操作）
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == ContentStatus.PUBLISHED and not self.published_at:
            self.published_at = datetime.now()
            if reviewer_id:
                self.reviewer_id = reviewer_id
    
    def increment_view_count(self):
        """
        增加浏览次数
        """
        self.view_count += 1
        self.last_viewed_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 更新热度评分
        self._update_trending_score()
    
    def add_like(self):
        """
        增加点赞数
        """
        self.like_count += 1
        self.updated_at = datetime.now()
        self._update_trending_score()
    
    def remove_like(self):
        """
        减少点赞数
        """
        if self.like_count > 0:
            self.like_count -= 1
            self.updated_at = datetime.now()
            self._update_trending_score()
    
    def add_share(self):
        """
        增加分享次数
        """
        self.share_count += 1
        self.updated_at = datetime.now()
        self._update_trending_score()
    
    def add_bookmark(self):
        """
        增加收藏数
        """
        self.bookmark_count += 1
        self.updated_at = datetime.now()
    
    def remove_bookmark(self):
        """
        减少收藏数
        """
        if self.bookmark_count > 0:
            self.bookmark_count -= 1
            self.updated_at = datetime.now()
    
    def add_rating(self, rating: float):
        """
        添加评分
        
        Args:
            rating: 评分(1-5)
        """
        if self.average_rating is None:
            self.average_rating = rating
            self.rating_count = 1
        else:
            total_score = self.average_rating * self.rating_count + rating
            self.rating_count += 1
            self.average_rating = round(total_score / self.rating_count, 2)
        
        self.updated_at = datetime.now()
        self._update_quality_score()
    
    def mark_helpful(self):
        """
        标记为有用
        """
        self.helpful_count += 1
        self.updated_at = datetime.now()
        self._update_quality_score()
    
    def _update_trending_score(self):
        """
        更新热度评分
        """
        # 简化的热度计算：基于最近的互动
        days_since_published = 1
        if self.published_at:
            days_since_published = max(1, (datetime.now() - self.published_at).days)
        
        # 热度评分 = (浏览数 + 点赞数*5 + 分享数*10) / 发布天数
        self.trending_score = (
            self.view_count + 
            self.like_count * 5 + 
            self.share_count * 10
        ) / days_since_published
    
    def _update_quality_score(self):
        """
        更新质量评分
        """
        # 质量评分基于评分、有用评价等
        score = 0
        
        if self.average_rating:
            score += self.average_rating * 20  # 评分权重
        
        if self.rating_count > 0:
            helpful_rate = self.helpful_count / max(1, self.rating_count)
            score += helpful_rate * 30  # 有用率权重
        
        # 内容完整性评分
        completeness = 0
        if self.summary: completeness += 10
        if self.cover_image: completeness += 10
        if self.tags: completeness += 10
        if self.meta_description: completeness += 10
        
        score += completeness
        
        self.quality_score = min(100, score)
    
    def calculate_engagement_rate(self):
        """
        计算互动率
        
        Returns:
            互动率百分比
        """
        if self.view_count == 0:
            return 0
        
        engagements = self.like_count + self.share_count + self.comment_count
        return round(engagements / self.view_count * 100, 2)
    
    def is_popular(self, view_threshold=1000, rating_threshold=4.0):
        """
        判断是否为热门内容
        
        Args:
            view_threshold: 浏览量阈值
            rating_threshold: 评分阈值
            
        Returns:
            是否为热门内容
        """
        return (
            self.view_count >= view_threshold and
            (self.average_rating or 0) >= rating_threshold
        )
    
    def is_recent(self, days=7):
        """
        判断是否为最新内容
        
        Args:
            days: 天数阈值
            
        Returns:
            是否为最新内容
        """
        if not self.published_at:
            return False
        
        return (datetime.now() - self.published_at).days <= days
    
    def get_reading_progress_time(self, words_per_minute=200):
        """
        计算阅读进度时间
        
        Args:
            words_per_minute: 每分钟阅读字数
            
        Returns:
            预计阅读时间（分钟）
        """
        if self.word_count:
            return max(1, round(self.word_count / words_per_minute))
        return self.reading_time or 5
    
    def add_tag(self, tag: str):
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        if self.tags is None:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """
        移除标签
        
        Args:
            tag: 标签名称
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def is_suitable_for_user(self, user_age=None, user_conditions=None):
        """
        判断内容是否适合特定用户
        
        Args:
            user_age: 用户年龄
            user_conditions: 用户健康状况列表
            
        Returns:
            是否适合该用户
        """
        # 检查年龄范围
        if user_age and self.age_range:
            # 简化处理，实际应该解析年龄范围字符串
            pass
        
        # 检查健康状况匹配
        if user_conditions and self.health_conditions:
            for condition in user_conditions:
                if condition in self.health_conditions:
                    return True
        
        # 默认适合普通用户
        return self.target_audience == TargetAudience.GENERAL