package cn.edu.wyu.chatweb.Controller;

import cn.edu.wyu.chatweb.entity.Result;
import cn.edu.wyu.chatweb.entity.Session;
import cn.edu.wyu.chatweb.service.SessionService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/session")
@Slf4j
public class SessionController {
    @Autowired
    private SessionService sessionService;

    @GetMapping("/getSessions")
    public Result<List<Session>> getSessions(@RequestParam int userId) {
        return Result.success(sessionService.getSessionsByUserId(userId));
    }

    @PostMapping("/add")
    public Result<Session> addSession(@RequestBody Session session) {
       System.out.print(session);
        sessionService.addSession(session);
        return Result.success("添加成功");
    }

    @DeleteMapping("/del")
    public Result<String> delSession(@RequestParam int id) {
        sessionService.delSession(id);
        return Result.success("删除成功");
    }

}
