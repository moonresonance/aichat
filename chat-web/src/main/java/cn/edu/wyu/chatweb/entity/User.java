package cn.edu.wyu.chatweb.entity;

import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
@TableName("user")
public class User {
   private Integer id ;

   private String name;
   @NotNull(message = "密码不能为空")
   @Size(min = 6, max = 20, message = "密码长度必须在6-20之间")
   private String password;


   private String icon;

   @TableLogic
   private Integer deleted;

}


