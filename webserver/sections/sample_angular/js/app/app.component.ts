import { Component } from '@angular/core';

@Component({
  selector: 'my-app',
  template: '<h1>{{title}}</h1><h2>{{description}}!</h2>',
})
export class AppComponent {
  title = 'Angular2';
  description = 'application loaded';
}
