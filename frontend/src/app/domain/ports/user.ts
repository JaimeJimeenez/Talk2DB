import { User } from "@domain/models/user";
import { Observable } from "rxjs";

export abstract class UserPort {
    abstract signup(username: string, email: string, password: string): Observable<User>;
    abstract login(email: string, password: string): Observable<User>;
}
