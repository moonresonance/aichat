package cn.edu.wyu.chatweb.Controller;

import cn.edu.wyu.chatweb.entity.Chat;
import cn.edu.wyu.chatweb.entity.Result;
import cn.edu.wyu.chatweb.service.ChatService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@CrossOrigin(value = "*",maxAge = 360)
@Slf4j
@RequestMapping("/chat")
public class ChatController {
    @Autowired
    private ChatService chatService;

    @GetMapping("/getChats")
    public Result<List<Chat>> getChats(@RequestParam Integer userId, @RequestParam Integer sessionId){
        List<Chat> chats = chatService.getUserChatsAndSessionId(userId, sessionId);
        return Result.success(chats);
    }

    @PostMapping("/addChat")
    public Result<Chat> addChat(@RequestBody Chat chat){
        chatService.insertChat(chat);
        return Result.success("添加成功");
    }

    @DeleteMapping("/deleteChat")
    public Result<Chat> deleteChat(@RequestParam int sessionId){
        chatService.deleteChaBySessionId(sessionId);
        return Result.success("删除成功");
    }

    @PutMapping("/updateChat")
    public Result<Chat> updateChat(@RequestBody Chat chat) {

        chatService.updataChat(chat);
        return Result.success("更新成功");
    }

}
