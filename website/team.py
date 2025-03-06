from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from .models import Team, TeamMembers
from . import db


Teams = Blueprint('Teams', __name__)


@Teams.route('/event/<int:event_id>/add_team', methods=['GET', 'POST'])
@login_required
def add_new_team(event_id):
    # Check if the current user is authorized (admin with id=1)
    if current_user.id != 1:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'GET':
        return render_template("/Event Management/Team Management/team_edit.html", event_id=event_id)

    if request.method == 'POST':
        team_name = request.form.get('team_name')
        captain_name = request.form.get('captain_name')
        players_names = request.form.getlist('players_name[]')
        players_sex = request.form.getlist('players_sex[]')
        players_level = request.form.getlist('players_level[]')

        # Validate form data
        if not team_name or not captain_name:
            flash('Please fill in all required fields!', category='error')
            return redirect(url_for('Teams.add_new_team'))
        
        # Check if a team with the same name already exists for the event
        existing_team = Team.query.filter_by(team_name=team_name, event_id=event_id).first()
        if existing_team:
            flash('A team with this name already exists for this event!', category='error')
            return redirect(url_for('Teams.add_new_team', event_id=event_id))

        # Create a new Team object
        new_team = Team(team_name=team_name, captain_name=captain_name, admin_id=current_user.id, event_id=event_id)  # Assuming event_id is known

        # Add the team to the session
        db.session.add(new_team)
        db.session.commit()  # Commit to get the team ID

        # Add team members
        for name, sex, level in zip(players_names, players_sex, players_level):
            if name:  # Ensure the player name is not empty
                new_member = TeamMembers(name=name, level=level, gender=sex, team_id=new_team.id)
                db.session.add(new_member)

        # Commit all changes
        try:
            db.session.commit()
            flash('Team added successfully!', category='success')
            return redirect(url_for('add_event.event_page', event_id=event_id))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", category='error')
            return redirect(url_for('Teams.add_new_team'))


@Teams.route('/view_teams', methods=['GET'])
@login_required
def view_teams():
    # Fetch all teams from the database
    teams = Team.query.all()
    return render_template('view_teams.html', teams=teams)


@Teams.route('/edit_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    # Ensure the user is an admin
    if current_user.id != 1:
        flash("You do not have permission to access this page.", category='error')
        return redirect(url_for('Teams.view_teams'))

    # Fetch the team by ID
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        # Extract form data
        team_name = request.form.get('team_name')
        captain_name = request.form.get('captain_name')
        players_names = request.form.getlist('players_name[]')
        players_sex = request.form.getlist('players_sex[]')
        players_level = request.form.getlist('players_level[]')

        # Validate form data
        if not team_name or not captain_name:
            flash('Please fill in all required fields!', category='error')
        else:
            # Check if a team with the same name already exists for the event, excluding the current team
            existing_team = Team.query.filter(Team.team_name == team_name, Team.event_id == team.event_id, Team.id != team_id).first()
            if existing_team:
                flash('A team with this name already exists for this event!', category='error')
                return redirect(url_for('Teams.edit_team', team_id=team_id))

            try:
                # Update team details
                team.team_name = team_name
                team.captain = captain_name

                # Clear existing team members
                TeamMembers.query.filter_by(team_id=team.id).delete()

                # Add updated team members
                for name, sex, level in zip(players_names, players_sex, players_level):
                    if name:  # Ensure the player name is not empty
                        new_member = TeamMembers(name=name, designation=sex, year=level, team_id=team.id)
                        db.session.add(new_member)

                db.session.commit()
                flash('Team updated successfully!', category='success')
                return redirect(url_for('Teams.view_teams'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", category='error')

    return render_template('edit_team.html', team=team)


@Teams.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    # Ensure the user is an admin
    if current_user.id != 1:
        flash("You do not have permission to access this action.", category='error')
        return redirect(url_for('Teams.view_teams'))

    team = Team.query.get_or_404(team_id)
    try:
        db.session.delete(team)
        db.session.commit()
        flash('Team deleted successfully!', category='success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", category='error')

    return redirect(url_for('Teams.view_teams'))