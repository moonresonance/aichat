package cn.edu.wyu.chatweb.entity;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;

@Data
public class Chat {

    private Integer id;

    @TableField("session_id")
    private Integer sessionId;

    @TableField("user_id")
    private Integer userId;
    private String role;
    private String content;
}
