#!usr/bin/env python
# -*- coding:utf-8 _*-
# Create by hex7 at 11/22/18
#

from flask import render_template, session, redirect, url_for, flash, abort
from flask import request, current_app, make_response, jsonify
from flask_paginate import Pagination
# from flask_login import login_required
# from flask_login import current_user
from . import main
# from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import TRTFailedRecord


# from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    #     form = PostForm()
    #     if current_user.can(Permission.WRITE) and form.validate_on_submit():
    #         post = Post(body=form.body.data,
    #                     author=current_user._get_current_object())
    #         db.session.add(post)
    #         db.session.commit()
    #         return redirect(url_for('.index'))
    #     # posts = Post.query.order_by(Post.timestamp.desc()).all()
    #     page = request.args.get('page', 1, type=int)
    #     show_followed = False
    #     if current_user.is_authenticated:
    #         show_followed = bool(request.cookies.get('show_followed', ''))
    #     if show_followed:
    #         query = current_user.followed_posts
    #     else:
    #         query = Post.query
    #     print(current_app.config)
    #     per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    #     pagination = query.order_by(Post.timestamp.desc()).paginate(
    #         page, per_page=per_page,
    #         error_out=False)
    #     posts = pagination.items
    version_list = get_versions()

    page = request.args.get('page', 1, type=int)
    trt = request.args.get('tensorrt', '')
    version = request.args.get('version', '')
    cuda = request.args.get('cuda', '')
    gpu = request.args.get('gpu', '')
    os = request.args.get('os', '')
    arch = request.args.get('arch', '')
    category = request.args.get('category', '')
    case_name = request.args.get('case_name', '')

    per_page = current_app.config['RECORD_PER_PAGE']

    if len(version) == 0 and len(version_list) > 0:
        version = version_list[0]

    data, count = get_data(page, per_page, version, trt, cuda, gpu, os,
                           arch, category, case_name)

    pagination = Pagination(page=page, per_page=per_page, total=count)

    result = get_filter_data(version, trt, cuda, gpu, os)

    trt_list = result['trt']
    arch_list = result.get('arch')
    cuda_list = result.get('cuda')
    gpu_list = result.get('gpu')
    os_list = result.get('os')
    category_list = result.get('category')
    case_list = result.get('cases')

    data = data.items

    return render_template('index.html', data=data,
                           version_list=version_list, selected_version=version,
                           trt_list=trt_list, selected_trt=trt,
                           cuda_list=cuda_list, selected_cuda=cuda,
                           gpu_list=gpu_list, selected_gpu=gpu,
                           os_list=os_list, selected_os=os,
                           arch_list=arch_list, selected_arch=arch,
                           category_list=category_list,
                           selected_category=category,
                           case_list=case_list, selected_case=case_name,
                           pagination=pagination)


@main.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        id = request.form['id']
        category = request.form['category']
        nvbug = request.form['nvbug']

        TRTFailedRecord.update_case(id, category, nvbug)

    return jsonify('save ok.')


@main.route('/batch_edit_bug', methods=['GET', 'POST'])
def batch_edit_bug():
    if request.method == 'POST':
        ids = request.form['ids']
        nvbug = request.form['nvbug']

        if len(ids) == 0:
            return jsonify('update bug failed.')

        for id in ids.split(","):
            TRTFailedRecord.update_case(id=id, nvbug=nvbug)

    return jsonify('update bug ok.')


@main.route('/batch_edit_category', methods=['GET', 'POST'])
def batch_edit_category():
    if request.method == 'POST':
        ids = request.form['ids']
        category = request.form['category']

        if len(ids) == 0:
            flash('Please choose one item.')
            return jsonify('update category failed.')

        for id in ids.split(","):
            TRTFailedRecord.update_case(id=id, category=category)

    return jsonify('update category ok.')


def get_filter_data(version, trt, cuda, gpu, os):
    trt_list = get_trt(version)
    cuda_list = get_cuda(version, trt)
    gpu_list = get_gpu(version, trt, cuda)
    os_list = get_os(version, trt, cuda)
    arch_list = get_arch(version, trt, os)
    category_list = get_category(version)
    case_list = get_cases(version, trt, cuda, gpu)

    output = {
        'trt': trt_list,
        'cuda': cuda_list,
        'gpu': gpu_list,
        'os': os_list,
        'arch': arch_list,
        'category': category_list,
        'cases': case_list
    }

    return output


def get_versions():
    result = TRTFailedRecord.query.distinct(
        TRTFailedRecord.version).order_by(TRTFailedRecord.version.desc())

    output = [item.version for item in result]

    return output


def get_trt(version):
    result = TRTFailedRecord.query.distinct(
        TRTFailedRecord.trt).filter_by(
        version=version).order_by(TRTFailedRecord.trt.desc())

    output = [item.trt for item in result]

    return output


def get_cuda(version, trt=''):
    if len(trt) == 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.cuda).filter_by(
            version=version).order_by(TRTFailedRecord.cuda.desc())
    else:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.cuda).filter_by(
            version=version, trt=trt).order_by(TRTFailedRecord.cuda.desc())

    output = [item.cuda for item in result]

    return output


def get_gpu(version, trt='', cuda=''):
    if len(trt) == 0 and len(cuda) == 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.platform).filter_by(
            version=version).order_by(TRTFailedRecord.platform.desc())
    elif len(cuda) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.platform).filter_by(
            version=version, trt=trt).order_by(TRTFailedRecord.platform.desc())
    elif len(trt) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.platform).filter_by(
            version=version, cuda=cuda).order_by(
            TRTFailedRecord.platform.desc())
    else:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.platform).filter_by(
            version=version, trt=trt, cuda=cuda).order_by(
            TRTFailedRecord.platform.desc())

    output = [item.platform for item in result]

    return output


def get_os(version, trt='', cuda=''):
    if len(trt) == 0 and len(cuda) == 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.os).filter_by(
            version=version)
    elif len(cuda) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.os).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.os).filter_by(version=version, cuda=cuda)
    else:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.os).filter_by(version=version, trt=trt, cuda=cuda)

    output = [item.os for item in result]

    return output


def get_arch(version, trt='', os=''):
    if len(trt) == 0 and len(os) == 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.arch).filter_by(
            version=version)
    elif len(os) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.arch).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(os) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.arch).filter_by(version=version, os=os)
    else:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.arch).filter_by(version=version, trt=trt, os=os)

    output = [item.arch for item in result]

    return output


def get_cases(version, trt='', cuda='', gpu=''):
    if len(trt) == 0 and len(cuda) == 0 and len(gpu) == 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(
            version=version)
    elif len(cuda) == 0 and len(gpu) == 0 and len(trt) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, trt=trt)
    elif len(trt) == 0 and len(gpu) == 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, cuda=cuda)
    elif len(trt) == 0 and len(cuda) == 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, platform=gpu)
    elif len(trt) == 0 and len(cuda) != 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, cuda=cuda,
                                                 platform=gpu)
    elif len(cuda) == 0 and len(trt) != 0 and len(gpu) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, trt=trt,
                                                 platform=gpu)
    elif len(gpu) == 0 and len(trt) != 0 and len(cuda) != 0:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.case_name).filter_by(version=version, trt=trt,
                                                 cuda=cuda)
    else:
        result = TRTFailedRecord.query.distinct(
            TRTFailedRecord.arch).filter_by(version=version, trt=trt, cuda=cuda,
                                            platform=gpu)

    output = [item.case_name for item in result]

    return output


def get_category(version):
    result = TRTFailedRecord.query.distinct(
        TRTFailedRecord.category).filter_by(
        version=version)

    output = [item.category for item in result]

    return output


def get_data(page, per_page, version, trt='', cuda='', gpu='', os='', arch='',
             category='', case_name=''):
    if len(trt) == 0:
        trt_list = get_trt(version=version)
    else:
        trt_list = [trt]

    if len(cuda) == 0:
        cuda_list = get_cuda(version=version, trt=trt)
    else:
        cuda_list = [cuda]

    if len(gpu) == 0:
        gpu_list = get_gpu(version=version, trt=trt, cuda=cuda)
    else:
        gpu_list = [gpu]

    if len(os) == 0:
        os_list = get_os(version=version, trt=trt, cuda=cuda)
    else:
        os_list = [os]

    if len(arch) == 0:
        arch_list = get_arch(version=version, trt=trt, os=os)
    else:
        arch_list = [arch]

    if len(category) == 0:
        category_list = get_category(version=version)
    else:
        category_list = [category]

    if len(case_name) == 0:
        case_list = get_cases(version=version, trt=trt, cuda=cuda, gpu=gpu)
    else:
        case_list = [case_name]

    query = TRTFailedRecord.query

    data = query.filter(
        TRTFailedRecord.trt.in_(trt_list),
        TRTFailedRecord.platform.in_(gpu_list),
        TRTFailedRecord.os.in_(os_list),
        TRTFailedRecord.arch.in_(arch_list),
        TRTFailedRecord.category.in_(category_list),
        TRTFailedRecord.case_name.in_(case_list),
        TRTFailedRecord.cuda.in_(cuda_list)).order_by(
        TRTFailedRecord.id.asc()).paginate(
        page, per_page=per_page,
        error_out=False)

    count = query.filter(TRTFailedRecord.trt.in_(trt_list),
                         TRTFailedRecord.platform.in_(gpu_list),
                         TRTFailedRecord.os.in_(os_list),
                         TRTFailedRecord.arch.in_(arch_list),
                         TRTFailedRecord.category.in_(category_list),
                         TRTFailedRecord.case_name.in_(case_list),
                         TRTFailedRecord.cuda.in_(cuda_list)).count()

    return data, count

# @main.route('/user/<username>', methods=['GET', 'POST'])
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     if user is None:
#         abort(404)
#     # posts = user.posts.order_by(Post.timestamp.desc()).all()
#     per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
#     page = request.args.get('page', 1, type=int)
#     pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
#         page, per_page=per_page,
#         error_out=False)
#     posts = pagination.items
#     return render_template('user.html', user=user, posts=posts,
#                            pagination=pagination)


# @main.route('/edit-profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.name = form.name.data
#         current_user.location = form.location.data
#         current_user.about_me = form.about_me.data
#         db.session.add(current_user._get_current_object())
#         db.session.commit()
#         flash('Your profile has been updated.')
#         return redirect(url_for('.user', username=current_user.username))

#     form.name.data = current_user.name
#     form.location.data = current_user.location
#     form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', form=form)


# @main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def edit_profile_admin(id):
#     user = User.query.get_or_404(id)
#     form = EditProfileAdminForm(user=user)
#     if form.validate_on_submit():
#         user.email = form.email.data
#         user.username = form.username.data
#         user.confirmed = form.confirmed.data
#         user.role = Role.query.get(form.role.data)
#         user.name = form.name.data
#         user.location = form.location.data
#         user.about_me = form.about_me.data
#         db.session.add(user)
#         db.session.commit()
#         flash('The profile has been updated.')
#         return redirect(url_for('.user', username=user.username))

#     form.email.data = user.email
#     form.username.data = user.username
#     form.confirmed.data = user.confirmed
#     form.role.data = user.role_id
#     form.name.data = user.name
#     form.location.data = user.location
#     form.about_me.data = user.about_me
#     return render_template('edit_profile.html', form=form, user=user)


# @main.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit(id):
#     post = Post.query.get_or_404(id)
#     if current_user != post.author and \
#             not current_user.can(Permission.ADMIN):
#         abort(403)
#     form = PostForm()
#     if form.validate_on_submit():
#         post.body = form.body.data
#         db.session.add(post)
#         db.session.commit()
#         flash('The post has been updated.')
#         return redirect(url_for('.post', id=post.id))

#     form.body.data = post.body
#     return render_template('edit_post.html', form=form)


# @main.route('/all')
# @login_required
# def show_all():
#     resp = make_response(redirect(url_for('.index')))
#     resp.set_cookie('show_followed', '', max_age=30*24*60*60)
#     return resp
